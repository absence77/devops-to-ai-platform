"""
Claude MCP Agent — Kubernetes Assistant
Answers questions in Russian and English
using real cluster data via MCP
"""

import asyncio
import pathlib
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import anthropic

SYSTEM_PROMPT = """You are a Kubernetes cluster assistant.
You have access to tools to inspect a real production Kubernetes cluster.
Always use tools to get real data before answering.
Answer in the same language the user asked the question.
Be concise and highlight any problems you find."""

async def ask_cluster(question: str):
    server_params = StdioServerParameters(
        command="python3",
        args=[str(pathlib.Path(__file__).parent.parent / "servers" / "kubectl_server.py")]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            tools = [
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema
                }
                for t in tools_result.tools
            ]

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            messages = [{"role": "user", "content": question}]

            print(f"\nQuestion: {question}")
            print("-" * 60)

            while True:
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=SYSTEM_PROMPT,
                    tools=tools,
                    messages=messages
                )

                if response.stop_reason == "tool_use":
                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"  🔧 {block.name}({block.input})")
                            result = await session.call_tool(block.name, block.input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result.content[0].text
                            })
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({"role": "user", "content": tool_results})
                else:
                    for block in response.content:
                        if hasattr(block, "text"):
                            print(f"\n{block.text}")
                    break

async def main():
    questions = [
        "Show me the status of all nodes and pods in production",
        "Are there any recent warning events in production namespace?",
        "Are there any pods with errors or restarts?",
    ]

    for q in questions:
        await ask_cluster(q)
        print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
