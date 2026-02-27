# Installation

## One Command Install (Recommended)

```bash
curl -fsSL https://agentsforge.dev/install.sh | bash
```

That's it. The installer handles everything automatically:

1. **Auto-installs prerequisites** — git, Python 3.12, Node.js 20.x (Ubuntu/Debian via apt; macOS via Homebrew check)
2. **Detects or installs OpenClaw** — if no AI agent platform is found, prompts to install OpenClaw
3. **Configures your AI model** — interactive wizard (`openclaw configure --section model`) to pick your provider + API key
4. **Clones and installs AgentForge** — into `~/.agentforge` with isolated venv
5. **Initializes and starts** — `agentforge init` + `agentforge start` automatically
6. **Confirms bot is running** — `agentforge status` check with clear pass/fail output

### Install Flow

```
curl -fsSL https://agentsforge.dev/install.sh | bash

→ Checks Ubuntu/Debian apt (or macOS Homebrew)
→ Auto-installs: git, python3.12, python3.12-venv, nodejs 20.x
→ Detects: is OpenClaw installed?
  → If NOT: "Install OpenClaw? [Y/n]"
    → Y: npm install -g openclaw
    → Runs: openclaw configure --section model  ← YOU PICK YOUR AI MODEL HERE
→ agentforge init --platform openclaw
→ agentforge start
→ ✅ "AgentForge is installed and running!"
→ Test: openclaw chat
```

### Install Options

```bash
# Include Agent Mailbox for multi-agent coordination
curl -fsSL https://agentsforge.dev/install.sh | bash -s -- --mailbox

# Force upgrade existing installation
curl -fsSL https://agentsforge.dev/install.sh | bash -s -- --upgrade

# Custom install location
AGENTFORGE_HOME=/opt/agentforge curl -fsSL https://agentsforge.dev/install.sh | bash

# Force OpenClaw install in CI (skips interactive model config — run manually after)
INSTALL_OPENCLAW=1 CI=true curl -fsSL https://agentsforge.dev/install.sh | bash
```

---

## AI Model Setup (OpenClaw)

During install, you'll be prompted to configure your AI model. You'll need an API key from one of:

| Provider | Model | Where to get a key |
|----------|-------|-------------------|
| **Anthropic** ⭐ recommended | Claude | [anthropic.com](https://anthropic.com) |
| **OpenAI** | GPT-4 | [platform.openai.com](https://platform.openai.com) |
| **xAI** | Grok | [x.ai/api](https://x.ai/api) |
| **Groq** | Llama 3 | [groq.com](https://groq.com) (free tier) |

To reconfigure after install:

```bash
openclaw configure --section model
```

---

## OS Requirements

| OS | Support |
|----|---------|
| **Ubuntu 20.04+** / Debian | ✅ Auto-installs all prerequisites |
| **macOS** (with Homebrew) | ✅ Checks prerequisites, guides if missing |
| **Windows** | ⚠️ Use WSL2 (Ubuntu) — see below |
| **Other Linux** | ⚠️ Manual prerequisite install required |

### Windows (WSL2)

```powershell
# In PowerShell as Administrator:
wsl --install
# Then open Ubuntu and run the one-liner
```

### macOS (Homebrew)

If Homebrew is installed, the installer checks your tools. If any are missing:

```bash
brew install git python@3.12 node
```

---

## Prerequisites (auto-installed on Ubuntu/Debian)

- **git** — for cloning repos
- **Python 3.12+** — with `venv` module (via deadsnakes PPA if needed)
- **Node.js 20.x** — for OpenClaw (via NodeSource if needed)
- **pip** — Python package manager

---

## npm Package (Node.js Projects)

For Node.js/TypeScript projects, use the HealthKit npm package:

```bash
npm install @agentsforge/healthkit
```

```javascript
import { HealthKit } from '@agentsforge/healthkit';

const health = new HealthKit();
await health.check();
```

## pip Package (Python Projects)

```bash
pip install agentforge
```

Then initialize and start:

```bash
agentforge init      # Configure platform and components
agentforge start     # Launch services
agentforge status    # Check what's running
agentforge doctor    # Diagnose issues
```

---

## Agent Mailbox (Multi-Agent Coordination)

For multi-agent systems, install the Agent Mailbox:

```bash
git clone https://github.com/JakebotLabs/agent-mailbox.git ~/.openclaw/mailbox
cd ~/.openclaw/mailbox
python mailbox.py --agent <your-agent-id> onboard
```

Or include it during install:

```bash
curl -fsSL https://agentsforge.dev/install.sh | bash -s -- --mailbox
```

---

## Platform Detection

The installer automatically detects your agent platform:

| Platform | Detection | Behavior |
|----------|-----------|----------|
| **OpenClaw** | `openclaw` command + `~/.openclaw/openclaw.json` | Uses existing workspace paths + prompts model config |
| **LangChain** | `import langchain` succeeds | Configures LangChain integration |
| **Standalone** | Default | Full isolation in `~/.agentforge` |

---

## Manual Installation

If the one-liner doesn't work for your environment:

```bash
# 1. Install prerequisites manually
sudo apt-get install git python3.12 python3.12-venv python3-pip nodejs npm

# 2. Install OpenClaw (recommended)
npm install -g openclaw
openclaw configure --section model

# 3. Clone and install AgentForge
git clone https://github.com/JakebotLabs/agentforge.git ~/.agentforge/repo
python3.12 -m venv ~/.agentforge/venv
~/.agentforge/venv/bin/pip install ~/.agentforge/repo

# 4. Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
mkdir -p ~/.local/bin
echo '#!/bin/bash' > ~/.local/bin/agentforge
echo 'exec ~/.agentforge/venv/bin/agentforge "$@"' >> ~/.local/bin/agentforge
chmod +x ~/.local/bin/agentforge
source ~/.bashrc

# 5. Initialize and start
agentforge init --platform openclaw
agentforge start
agentforge doctor
```

---

## Troubleshooting

### "agentforge command not found"

The command is installed to `~/.local/bin`. Either:

```bash
# Add to current session
export PATH="$HOME/.local/bin:$PATH"

# Or open a new terminal
```

### "openclaw: No such model configured"

The model setup step was skipped. Fix it:

```bash
openclaw configure --section model
```

### Python version too old

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update && sudo apt-get install python3.12 python3.12-venv

# macOS
brew install python@3.12
```

### Node.js / npm missing

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node
```

### "Permission denied"

Don't run with `sudo`. The installer uses `~/.local/bin` and `~/.agentforge` which don't require root.

---

## Uninstall

```bash
rm -rf ~/.agentforge
rm ~/.local/bin/agentforge
# Optionally: npm uninstall -g openclaw
```

---

**Need help?** Open an issue at [github.com/JakebotLabs/agentforge](https://github.com/JakebotLabs/agentforge/issues)
