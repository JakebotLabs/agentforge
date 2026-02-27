# Changelog

## [0.1.0] — 2026-02-27

### 🚀 First stable release

**What's in the box:**
- `agentforge init` — initialize agent infrastructure (OpenClaw, standalone, Docker)
- `agentforge start` — launch full stack (dashboard + healthkit + memory)
- `agentforge stop` — graceful shutdown
- `agentforge status` — component health at a glance
- `agentforge doctor` — diagnose installation issues
- `agentforge pipeline codebot|opusbot <task>` — Dev Pipeline (Pro)

**Components installed:**
- `agent-memory-core` — three-layer memory (Markdown + ChromaDB + NetworkX)
- `agent-healthkit` — health monitoring + soul drift detection
- `agent-mailbox` — async agent-to-agent coordination
- `jakebot-dashboard` — FastAPI + Preact web UI (port 7842)

**npm package:** `@agentsforge/healthkit@0.1.0` — TypeScript SDK for Node.js projects

**Platform support:** Linux, macOS, Windows (cross-platform runner + venv detection)

**CI:** ✅ Passing on ubuntu-22.04 and ubuntu-24.04

---

## [0.1.0a1] — 2026-02-18

- Initial alpha release
- Core CLI scaffolding
- OpenClaw platform adapter
