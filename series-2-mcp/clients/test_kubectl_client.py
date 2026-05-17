"""
MCP Client — тестируем kubectl MCP сервер
Подключается к серверу и вызывает все 3 инструмента
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    print("=" * 50)
    print("MCP kubectl client — connecting...")
    print("=" * 50)

    server_params = StdioServerParameters(
        command="python3",
        args=["/root/devops-to-ai-platform/series-2-mcp/servers/kubectl_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize session
            await session.initialize()
            print("Connected to MCP server!")

            # List available tools
            tools = await session.list_tools()
            print(f"\nAvailable tools: {[t.name for t in tools.tools]}")

            # Test 1: get_nodes
            print("\n--- TEST 1: get_nodes ---")
            result = await session.call_tool("get_nodes", {})
            print(result.content[0].text)

            # Test 2: get_pods
            print("\n--- TEST 2: get_pods (production) ---")
            result = await session.call_tool("get_pods", {"namespace": "production"})
            print(result.content[0].text)

            print("\n" + "=" * 50)
            print("MCP kubectl server works!")
            print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
