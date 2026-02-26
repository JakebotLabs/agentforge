# AgentForge

**Complete AI agent infrastructure in one command.**

AgentForge bundles persistent memory, health monitoring, and a live dashboard into a single deployable stack.

## Quick Start (OpenClaw)

```bash
pip install agentforge
agentforge init --platform openclaw
agentforge start
```

Dashboard: http://localhost:7842

## Quick Start (Docker)

```bash
git clone https://github.com/Jakebot-ops/agentforge
cd agentforge
docker-compose up -d
```

## Commands

| Command | Description |
|---------|-------------|
| `agentforge init` | Initialize AgentForge in current environment |
| `agentforge start` | Start all services |
| `agentforge stop` | Stop all services |
| `agentforge status` | Show component status |
| `agentforge doctor` | Diagnose installation issues |

## Configuration

Config file: `~/.agentforge/agentforge.yml`

```yaml
version: "1"
platform: openclaw
workspace: ~/.openclaw/workspace
memory:
  enabled: true
healthkit:
  enabled: true
  mode: observe
dashboard:
  enabled: true
  port: 7842
```

## What's Included

- **Persistent Memory** — Three-layer memory (Markdown + ChromaDB + NetworkX)
- **Agent HealthKit** — Runtime monitoring and auto-healing
- **Dashboard** — Web UI for memory search and health monitoring

## License

MIT — Free to use, modify, and distribute.

---

Built by [Jakebot Labs](https://jakebotlabs.com) · [GitHub](https://github.com/Jakebot-ops)
