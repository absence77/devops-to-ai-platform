"""
Judge Guard — safety layer for MCP write operations
From DevOps to AI Platform | Series 2 | Part 2

Встаёт между MCP клиентом и опасными инструментами.
Перед любым rollout_restart — Judge оценивает риск.
Score < 70 → команда заблокирована.
Score >= 70 → выполняется через MCP.
"""

import asyncio
import os
import json
import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

JUDGE_SYSTEM_PROMPT = """You are a Senior SRE acting as a safety reviewer.
Evaluate this Kubernetes action plan on 4 criteria, score each 0-100:

1. SAFETY: Will this cause harm or data loss? (100=safe, 0=catastrophic)
2. RELEVANCE: Does this fix the actual problem? (100=yes, 0=wrong fix)
3. RISK: Blast radius if it fails? (100=isolated pod, 0=entire cluster)
4. ALTERNATIVES: Is this the best approach? (100=optimal, 0=wrong)

VERDICT RULES:
- total_score >= 70 → APPROVE
- total_score 50-69 → ESCALATE
- total_score < 50  → REJECT

Respond ONLY with valid JSON:
{
  "safety_score": <int>,
  "relevance_score": <int>,
  "risk_score": <int>,
  "alternatives_score": <int>,
  "total_score": <int>,
  "verdict": "<APPROVE|REJECT|ESCALATE>",
  "reasoning": "<2 sentences>",
  "recommendation": "<specific suggestion if not APPROVE>"
}"""


def evaluate_with_judge(action: str, target: str, namespace: str) -> dict:
    """Judge оценивает действие перед выполнением через MCP."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    plan = f"""
ACTION: {action}
TARGET: {target}
NAMESPACE: {namespace}
COMMAND: kubectl {action.replace('_', ' ')} {target} -n {namespace}
"""

    print(f"\n🐙 JUDGE evaluating: {action} → {target} in {namespace}")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Evaluate this action:\n{plan}"}]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "safety_score": 0, "relevance_score": 0,
            "risk_score": 0, "alternatives_score": 0,
            "total_score": 0, "verdict": "ESCALATE",
            "reasoning": "Judge failed to parse. Manual review required.",
            "recommendation": "Review manually before executing."
        }

    emoji = {"APPROVE": "✅", "REJECT": "❌", "ESCALATE": "⚠️"}.get(result["verdict"], "❓")
    print(f"   {emoji} VERDICT: {result['verdict']} (score: {result['total_score']}/100)")
    print(f"   Reasoning: {result['reasoning']}")
    if result.get("recommendation"):
        print(f"   Recommend: {result['recommendation']}")

    return result


async def safe_rollout_restart(deployment: str, namespace: str = "production"):
    """
    Безопасный rollout restart через MCP + Judge.
    Judge проверяет → если APPROVE → MCP выполняет.
    """
    print(f"\n{'='*60}")
    print(f"SAFE ROLLOUT RESTART")
    print(f"Target: {deployment} / {namespace}")
    print(f"{'='*60}")

    # Шаг 1: Judge оценивает
    verdict = evaluate_with_judge("rollout_restart", deployment, namespace)

    if verdict["verdict"] == "REJECT":
        print(f"\n🛑 BLOCKED BY JUDGE — action cancelled")
        print(f"   Score: {verdict['total_score']}/100")
        return False

    if verdict["verdict"] == "ESCALATE":
        print(f"\n⚠️  JUDGE REQUIRES HUMAN APPROVAL")
        print(f"   Score: {verdict['total_score']}/100")
        confirm = input("   Proceed? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("   Cancelled by human.")
            return False

    # Шаг 2: Judge APPROVED → выполняем через MCP
    print(f"\n✅ JUDGE APPROVED — executing via MCP...")

    server_params = StdioServerParameters(
        command="python3",
        args=["/root/devops-to-ai-platform/series-2-mcp/servers/kubectl_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "rollout_restart",
                {"deployment": deployment, "namespace": namespace}
            )
            print(f"\n📋 Result: {result.content[0].text}")
            return True


async def main():
    print("=" * 60)
    print("TEST 1: Safe restart — monitoring-grafana")
    print("=" * 60)
    await safe_rollout_restart("monitoring-grafana", "production")

    print("\n" + "=" * 60)
    print("TEST 2: Dangerous — fake production-critical-db")
    print("=" * 60)

    # Симулируем опасный запрос
    verdict = evaluate_with_judge(
        "rollout_restart",
        "production-critical-db",
        "production"
    )
    if verdict["verdict"] != "APPROVE":
        print(f"\n🛑 Correctly blocked dangerous operation!")


if __name__ == "__main__":
    asyncio.run(main())
