"""
Claude MCP Agent — Kubernetes Assistant
Подключает Claude к kubectl MCP серверу.
Агент понимает вопросы на русском и английском.
"""

import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM_PROMPT = """You are a Kubernetes cluster assistant. 
You have access to tools to inspect a real production Kubernetes cluster.

When asked about the cluster — always use the tools to get real data.
Answer in the same language the user asked the question.
Be concise and highlight any problems you find.

If you see pods not in Running state — highlight them as issues.
If all pods are healthy — confirm that clearly."""

async def ask_cluster(question: str):
    """Задаёт вопрос Claude который использует MCP инструменты."""

    server_params = StdioServerParameters(
        command="python3",
        args=["/root/devops-to-ai-platform/series-2-mcp/servers/kubectl_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Получаем список инструментов от MCP сервера
            tools_result = await session.list_tools()

            # Конвертируем MCP инструменты в формат Anthropic
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                }
                for t in tools_result.tools
            ]

            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            messages = [{"role": "user", "content": question}]

            print(f"\nВопрос: {question}")
            print("-" * 50)

            # Agentic loop — Claude вызывает инструменты пока не ответит
            while True:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages
                )

                # Если Claude хочет вызвать инструмент
                if response.stop_reason == "tool_use":
                    tool_results = []

                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"  🔧 Calling: {block.name}({block.input})")

                            # Вызываем инструмент через MCP
                            result = await session.call_tool(
                                block.name,
                                block.input
                            )
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                            })

                    # Добавляем результаты в диалог
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })

                # Claude дал финальный ответ
                else:
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(f"\n{block.text}")
                    break

async def main():
    questions = [
        # Русский
        "Покажи мне все ноды кластера и их статус",
        # English
        "Are there any problems with pods in production namespace?",
    ]

    for question in questions:
        await ask_cluster(question)
        print("\n" + "=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
