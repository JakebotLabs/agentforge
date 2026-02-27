# AgentForge

[![CI](https://github.com/JakebotLabs/agentforge/actions/workflows/test.yml/badge.svg)](https://github.com/JakebotLabs/agentforge/actions)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/JakebotLabs?style=flat&logo=github&label=Sponsor)](https://github.com/sponsors/JakebotLabs)

**Complete AI agent infrastructure in one command.**

Give your AI agent persistent memory, self-healing health monitoring, and a management dashboard — in under 60 seconds.

```bash
curl -fsSL https://agentsforge.dev/install.sh | bash
```

**What happens:**
- 🔧 Auto-installs prerequisites (git, Python 3.12, Node.js) on Ubuntu/Debian
- 🤖 Detects or installs [OpenClaw](https://openclaw.dev) (free AI agent platform)
- 🔑 Guides you through model selection (`openclaw configure --section model`)
- 🚀 Initializes and starts AgentForge automatically
- ✅ Confirms your bot is running — `openclaw chat` to test

## What You Get

| Layer | Description | Status |
|-------|-------------|--------|
| 🧠 **Memory** | ChromaDB vectors + NetworkX knowledge graph | ✅ Free |
| 🩺 **Health** | Auto-monitoring + self-healing + soul drift detection | ✅ Free |
| 📊 **Dashboard** | Web UI for memory & health management | ✅ Free |
| 🔧 **NPM Package** | TypeScript client: `@agentsforge/healthkit` | ✅ Free |
| ⚙️ **Dev Pipeline** | CodeBot + OpusBot autonomous coding | 🔐 [Pro](https://github.com/sponsors/JakebotLabs) |

## Quick Start

### One-Line Install (Recommended)

```bash
curl -fsSL https://agentsforge.dev/install.sh | bash
```

The installer walks you through model selection — have your API key ready.

### Manual Install

```bash
# Install OpenClaw first (recommended platform)
npm install -g openclaw
openclaw configure --section model

# Then install AgentForge
git clone https://github.com/JakebotLabs/agentforge
cd agentforge
python3 -m venv venv
source venv/bin/activate
pip install -e .
agentforge init --platform openclaw
agentforge start
```

## Commands

```bash
agentforge init      # Initialize AgentForge (interactive platform selection)
agentforge install   # Install/update all components
agentforge start     # Start dashboard and services
agentforge stop      # Stop all services
agentforge status    # Show component status
agentforge doctor    # Diagnose installation issues
```

## Configuration

Config file: `~/.agentforge/agentforge.yml`

```yaml
version: "1"
platform: standalone  # openclaw | langchain | autogen | standalone

workspace: ~/.agentforge

memory:
  enabled: true
healthkit:
  enabled: true
  mode: observe  # observe | heal
dashboard:
  enabled: true
  port: 7842
```

## Free vs Pro

**Free (MIT License):**
- Persistent memory with semantic search
- Health monitoring with auto-healing
- Web dashboard at localhost:7842
- Works with any agent framework

**Pro ($25/mo via [GitHub Sponsors](https://github.com/sponsors/JakebotLabs)):**
- Everything in Free
- Dev Pipeline (CodeBot + OpusBot)
- Autonomous code writing and review
- Private repo access
- Priority support

## TypeScript/JavaScript SDK

Use AgentForge health monitoring from Node.js or browser:

```bash
npm install @agentsforge/healthkit
```

```typescript
import { HealthKit, ClusterManager } from '@agentsforge/healthkit';

// Monitor cluster health
const kit = new HealthKit();
const status = await kit.getStatus();
console.log(status.drift_risk);  // "0%"

// Manage clusters
const cluster = new ClusterManager(config);
await cluster.deploy();
```

See [@agentsforge/healthkit on npm](https://www.npmjs.com/package/@agentsforge/healthkit) for full docs.

## Platform Support

AgentForge works with any Python-based agent:

- **OpenClaw** — Full integration
- **LangChain** — Adapter included
- **AutoGen** — Adapter included
- **Standalone** — Raw Python, no framework

## Requirements

- Linux (Ubuntu/Debian auto-install), macOS (Homebrew check), or WSL2
- ~500MB disk space
- An API key from Anthropic, OpenAI, xAI, or Groq (for AI model)
- **Ubuntu/Debian:** Prerequisites (Python 3.12, Node.js, git) installed automatically

## Documentation

- [Website](https://agentsforge.dev)
- [Unlock Pipeline Guide](docs/unlock-pipeline.md) (for sponsors)
- [Ubuntu Install Notes](docs/ubuntu-install-issues.md)

## License

MIT — Free to use, modify, and distribute.

The Dev Pipeline is available to [GitHub Sponsors](https://github.com/sponsors/JakebotLabs) ($25/mo+).

---

Built by [Jakebot Labs](https://jakebotlabs.com) · [Sponsor](https://github.com/sponsors/JakebotLabs) · [Website](https://agentsforge.dev)
