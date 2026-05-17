"""
Test ChromaDB MCP Server
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python3",
        args=["/root/devops-to-ai-platform/series-2-mcp/servers/chromadb_server.py"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Tools: {[t.name for t in tools.tools]}")

            # Test 1: database stats
            print("\n--- TEST 1: get_incident_stats ---")
            result = await session.call_tool("get_incident_stats", {})
            print(result.content[0].text)

            # Test 2: semantic search
            print("\n--- TEST 2: search CrashLoopBackOff ---")
            result = await session.call_tool("search_incidents", {
                "query": "CrashLoopBackOff pod crash",
                "n_results": 2
            })
            print(result.content[0].text)

            # Test 3: recent incidents
            print("\n--- TEST 3: recent incidents ---")
            result = await session.call_tool("get_recent_incidents", {"n": 3})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
