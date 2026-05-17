# From DevOps to AI Platform

> **How I rebuilt my infrastructure around AI agents**  
> Real Kubernetes. Real failures. Real money.

[![Medium](https://img.shields.io/badge/Medium-Series-black?logo=medium)](https://medium.com/@ahmadgayibov)
[![GitHub](https://img.shields.io/badge/GitHub-absence77-181717?logo=github)](https://github.com/absence77)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Claude%20API-orange)](https://docs.anthropic.com)
[![MCP](https://img.shields.io/badge/Protocol-MCP-purple)](https://modelcontextprotocol.io)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.30.14-blue?logo=kubernetes)](https://kubernetes.io)

---

## What This Is

I am an IT Architect with 15 years of experience in Linux, DevOps, and Kubernetes.

This repository documents my journey of transforming a traditional DevOps infrastructure  
into an AI-native platform — step by step, on a real production cluster, with real costs.

**This is not a tutorial. This is a live engineering log.**

---

## The Journey

### Series 1 — AI Agents in Production (Parts 1–13) ✅ COMPLETED
*From zero to autonomous incident response*

| What was built | Result |
|---|---|
| Multi-agent pipeline: Detector → Researcher → Judge → Executor | $0.004/incident |
| RAG memory with ChromaDB | 22 incidents, 368 KB |
| LLM-as-a-Judge safety layer | Blocked `kubectl delete namespace production` Safety 0/100 |
| Grafana → Claude → kubectl → Telegram | 6 seconds end-to-end |
| Full disaster recovery after namespace deletion | 1 day, $0 data loss |
| **Total investment** | **$200 over 2 months** |
| **ROI vs Commercial AIOps** | **150x** |

👉 Full code: [github.com/absence77/ai-agents-production](https://github.com/absence77/ai-agents-production)  
👉 Full series: [medium.com/@ahmadgayibov](https://medium.com/@ahmadgayibov)

---

### Series 2 — MCP in Production (Parts 14+) 🚧 IN PROGRESS
*Model Context Protocol — the protocol that changes everything*

```
Before MCP:                    After MCP:
Agent → Python code            Agent → MCP Protocol
     → subprocess kubectl           → kubectl MCP server
     → ChromaDB client              → ChromaDB MCP server
     → Telegram requests            → Telegram MCP server
     → Grafana API                  → Grafana MCP server
```

**Why MCP matters:**  
MCP is the USB-C of AI agents. One standard protocol connects agents to any tool.  
97M SDK downloads/month. 17,000+ servers. Linux Foundation governance.  
The protocol war is over — MCP won.

**What we are building:**

| Part | Topic | Status |
|---|---|---|
| 14 | Why I stopped writing scripts and started building agents | 🔜 |
| 15 | MCP: the protocol that changed how my agents talk | 🔜 |
| 16 | Building a Kubernetes MCP server from scratch | 🔜 |
| 17 | When my agent poisoned itself: MCP security | 🔜 |
| 18 | A2A protocol: agents talking to agents | 🔜 |
| 19 | Call Center AI on K8s: real client, real money | 🔜 |
| 20 | The Platform Engineer's AI Stack: full picture | 🔜 |

---

## Infrastructure

```
Internet
    |
    v
JumpServer ──── kubectl ────> master-1
                                                    |
AI Server                                     worker-1
├── MCP servers (series-2-mcp/)               worker-2
├── AI agents (series-1-foundations/)
├── webhook_v2.py (FastAPI :8080)         namespace: production
├── ChromaDB (RAG memory)                 ├── Prometheus
└── OpenClaw (3 Telegram bots)            ├── Grafana 13.0.1
                                          └── AlertManager
```

**Hetzner Cloud · Helsinki eu-central · Kubernetes v1.30.14 · Calico CNI **

---

## Repository Structure

```
devops-to-ai-platform/
├── series-1-foundations/     # AI Agents in Production (Parts 1-13)
│   └── agents/               # Detector, Researcher, Judge, Executor
├── series-2-mcp/             # MCP in Production (Parts 14+)
│   ├── servers/              # MCP servers (kubectl, ChromaDB, Grafana)
│   └── clients/              # MCP clients and agent integrations
├── infrastructure/
│   ├── k8s/                  # Kubernetes manifests
│   └── monitoring/           # Prometheus + Grafana configs
├── docs/                     # Architecture docs, runbooks
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/absence77/devops-to-ai-platform.git
cd devops-to-ai-platform

# Install
pip install anthropic mcp chromadb fastapi uvicorn

# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Run first MCP server (coming in Part 16)
cd series-2-mcp/servers
python3 kubectl_mcp_server.py
```

---

## Key Numbers

| Metric | Value |
|---|---|
| Total investment (Series 1) | $200 |
| Cost per incident | $0.004 |
| Response time | 6 seconds |
| ROI vs Commercial AIOps | 150x |
| Infrastructure cost | $74.95/month |
| Incidents in RAG memory | 22 |
| Articles published | 13 |

---

## Tech Stack

- **AI:** Anthropic Claude API (claude-sonnet-4-6, claude-haiku-4-5)
- **Protocol:** Model Context Protocol (MCP)
- **Memory:** ChromaDB v1.5.8
- **Orchestration:** Kubernetes v1.30.14, Calico CNI
- **Monitoring:** Prometheus + Grafana + AlertManager
- **Infrastructure:** Hetzner Cloud (5 servers, Helsinki)
- **Language:** Python 3.12

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Ahmad Gayibov · IT Architect & AI Platform Engineer*  
[medium.com/@ahmadgayibov](https://medium.com/@ahmadgayibov) · [t.me/devops_to_ai](https://t.me/devops_to_ai)
