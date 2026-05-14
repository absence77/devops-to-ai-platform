"""
MCP Server — kubectl tools for Kubernetes
Part of: From DevOps to AI Platform | Series 2

Tools:
- get_pods(namespace)     → список подов
- get_nodes()             → состояние нод
- describe_pod(pod, ns)   → детали пода
"""

import subprocess
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Создаём MCP сервер
server = Server("kubectl-server")

def run_kubectl(args: list[str]) -> str:
    """Запускает kubectl команду и возвращает вывод."""
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return f"Error: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "Error: kubectl timeout (30s)"
    except FileNotFoundError:
        return "Error: kubectl not found"

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Список доступных инструментов."""
    return [
        types.Tool(
            name="get_pods",
            description="Get list of pods in a Kubernetes namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "Kubernetes namespace (default: production)",
                        "default": "production"
                    }
                }
            }
        ),
        types.Tool(
            name="get_nodes",
            description="Get status of all Kubernetes cluster nodes",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="describe_pod",
            description="Get detailed information about a specific pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Name of the pod"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace of the pod",
                        "default": "production"
                    }
                },
                "required": ["pod_name"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Выполняет инструмент по имени."""

    if name == "get_pods":
        ns = arguments.get("namespace", "production")
        output = run_kubectl(["get", "pods", "-n", ns, "-o", "wide"])
        return [types.TextContent(type="text", text=output)]

    elif name == "get_nodes":
        output = run_kubectl(["get", "nodes", "-o", "wide"])
        return [types.TextContent(type="text", text=output)]

    elif name == "describe_pod":
        pod = arguments.get("pod_name")
        ns = arguments.get("namespace", "production")
        output = run_kubectl(["describe", "pod", pod, "-n", ns])
        return [types.TextContent(type="text", text=output)]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    # server ready
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
