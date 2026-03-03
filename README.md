# AgentForge

**Complete AI agent infrastructure in one command — works with any Python agent framework.**

Persistent memory, health monitoring, and a live dashboard. Drop it into your existing agent stack or run it standalone.

```bash
pip install agentsforge
agentforge init
agentforge start
```

Dashboard: http://localhost:7842

---

## Supported Platforms

| Platform | Command | Notes |
|----------|---------|-------|
| **Standalone** | `agentforge init --platform standalone` | No framework required. Works with any Python agent. |
| **OpenClaw** | `agentforge init --platform openclaw` | Auto-detects workspace, integrates with OpenClaw config |
| **LangChain** | `agentforge init --platform langchain` | Hooks into LangChain memory and callback system |

Default: `standalone` — works everywhere.

---

## Quick Start

### Standalone (any agent framework)
```bash
pip install agentsforge
agentforge init
agentforge start
```

### OpenClaw
```bash
pip install agentsforge
agentforge init --platform openclaw
agentforge start
```

### LangChain
```bash
pip install agentsforge
agentforge init --platform langchain --workspace ./my_agent
agentforge start
```

### Docker
```bash
git clone https://github.com/JakebotLabs/agentforge
cd agentforge
docker-compose up -d
```

---

## Commands

| Command | Description |
|---------|-------------|
| `agentforge init [--platform]` | Initialize AgentForge (default: standalone) |
| `agentforge start` | Start all services |
| `agentforge stop` | Stop all services |
| `agentforge status` | Show component status |
| `agentforge doctor` | Diagnose installation issues |

---

## What's Included

- **Persistent Memory** — Three-layer memory system (Markdown + ChromaDB vector search + NetworkX knowledge graph). Agents remember context across sessions without custom infrastructure.
- **Agent HealthKit** — Runtime health monitoring. Detects context bloat, resource pressure, model failures. Observe-only by default.
- **Dashboard** — Web UI at localhost:7842. Search memory, view health status, inspect agent state.

---

## Configuration

Config at `~/.agentforge/agentforge.yml`:

```yaml
version: "1"
platform: standalone
workspace: ~/.agentforge/data
memory:
  enabled: true
healthkit:
  enabled: true
  mode: observe
dashboard:
  enabled: true
  port: 7842
```

---

## Why AgentForge?

Most agent frameworks solve the intelligence problem. Almost none solve the operations problem:

- Agents forget everything between sessions
- No visibility into what's happening at runtime
- No standard way to detect drift, bloat, or failures
- Every team builds their own monitoring from scratch

AgentForge is the ops layer. You bring the agent; we handle memory, health, and observability.

---

## Python API

```python
from agentforge import AgentForge

af = AgentForge(platform="standalone")
af.init()

# Store memory
af.memory.store("user prefers concise replies")

# Retrieve relevant context
context = af.memory.search("user preferences", n_results=3)

# Health check
health = af.healthkit.check()
print(health.grade)  # A, B, C, D, F
```

---

## License

MIT — [JakebotLabs](https://agentsforge.dev)
