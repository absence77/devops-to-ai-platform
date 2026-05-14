"""
MCP Server — kubectl tools for Kubernetes
From DevOps to AI Platform | Series 2 | Part 1

Tools:
- get_pods(namespace)              — список подов
- get_nodes()                      — состояние нод
- describe_pod(pod, ns)            — детали пода
- get_logs(pod, ns, lines)         — логи пода
- get_events(namespace)            — события namespace
- rollout_restart(deployment, ns)  — рестарт деплоймента
"""

import subprocess
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("kubectl-server")

def run_kubectl(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["kubectl"] + args,
            capture_output=True, text=True, timeout=30
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
    return [
        types.Tool(
            name="get_pods",
            description="Get list of pods in a Kubernetes namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "default": "production"}
                }
            }
        ),
        types.Tool(
            name="get_nodes",
            description="Get status of all Kubernetes cluster nodes",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="describe_pod",
            description="Get detailed information about a specific pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {"type": "string"},
                    "namespace": {"type": "string", "default": "production"}
                },
                "required": ["pod_name"]
            }
        ),
        types.Tool(
            name="get_logs",
            description="Get logs from a specific pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {"type": "string"},
                    "namespace": {"type": "string", "default": "production"},
                    "lines": {"type": "integer", "default": 50}
                },
                "required": ["pod_name"]
            }
        ),
        types.Tool(
            name="get_events",
            description="Get recent Kubernetes events in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "default": "production"}
                }
            }
        ),
        types.Tool(
            name="rollout_restart",
            description="Restart a Kubernetes deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment": {"type": "string"},
                    "namespace": {"type": "string", "default": "production"}
                },
                "required": ["deployment"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_pods":
        ns = arguments.get("namespace", "production")
        out = run_kubectl(["get", "pods", "-n", ns, "-o", "wide"])

    elif name == "get_nodes":
        out = run_kubectl(["get", "nodes", "-o", "wide"])

    elif name == "describe_pod":
        pod = arguments["pod_name"]
        ns = arguments.get("namespace", "production")
        out = run_kubectl(["describe", "pod", pod, "-n", ns])

    elif name == "get_logs":
        pod = arguments["pod_name"]
        ns = arguments.get("namespace", "production")
        lines = str(arguments.get("lines", 50))
        out = run_kubectl(["logs", pod, "-n", ns, "--tail", lines])

    elif name == "get_events":
        ns = arguments.get("namespace", "production")
        out = run_kubectl(["get", "events", "-n", ns, "--sort-by=.lastTimestamp"])

    elif name == "rollout_restart":
        dep = arguments["deployment"]
        ns = arguments.get("namespace", "production")
        out = run_kubectl(["rollout", "restart", f"deployment/{dep}", "-n", ns])

    else:
        out = f"Unknown tool: {name}"

    return [types.TextContent(type="text", text=out)]

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
