"""
MCP Server — ChromaDB RAG Memory
From DevOps to AI Platform | Series 2 | Part 2

Tools:
- search_incidents(query, n)     — semantic search across incidents
- get_recent_incidents(n)        — last N incidents chronologically
- get_incident_stats()           — memory database statistics
"""

import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

sys.path.insert(0, '/root/rag')

server = Server("chromadb-server")

def get_chroma_client():
    import chromadb
    return chromadb.PersistentClient(path="/root/rag/incident_db")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_incidents",
            description="Search past Kubernetes incidents by semantic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Describe the incident to search for"
                    },
                    "n_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_recent_incidents",
            description="Get the most recent incidents from memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of recent incidents",
                        "default": 5
                    }
                }
            }
        ),
        types.Tool(
            name="get_incident_stats",
            description="Get statistics about incident memory database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "search_incidents":
        query = arguments.get("query", "")
        n = arguments.get("n_results", 3)
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("k8s_incidents")
            count = collection.count()
            if count == 0:
                return [types.TextContent(type="text",
                    text="No incidents in memory yet.")]
            results = collection.query(
                query_texts=[query],
                n_results=min(n, count)
            )
            output = f"Found {len(results['documents'][0])} similar incidents:\n\n"
            for i, (doc, meta) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0]
            )):
                output += f"--- Incident {i+1} ---\n"
                output += f"{doc[:500]}\n"
                if meta:
                    output += f"Metadata: {json.dumps(meta, indent=2)}\n"
                output += "\n"
            return [types.TextContent(type="text", text=output)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "get_recent_incidents":
        n = arguments.get("n", 5)
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("k8s_incidents")
            count = collection.count()
            if count == 0:
                return [types.TextContent(type="text",
                    text="No incidents in memory yet.")]
            results = collection.get(limit=min(n, count))
            output = f"Last {len(results['documents'])} incidents:\n\n"
            for i, (doc, meta) in enumerate(zip(
                results['documents'],
                results['metadatas']
            )):
                output += f"--- Incident {i+1} ---\n"
                output += f"{doc[:300]}\n\n"
            return [types.TextContent(type="text", text=output)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    elif name == "get_incident_stats":
        try:
            client = get_chroma_client()
            collection = client.get_or_create_collection("k8s_incidents")
            count = collection.count()
            output = f"ChromaDB Incident Memory Stats:\n"
            output += f"Total incidents: {count}\n"
            output += f"Database path: /root/rag/incident_db\n"
            output += f"Collection: incidents\n"
            return [types.TextContent(type="text", text=output)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
