# Ubuntu Clean Install Issues

Tracking issues hit on fresh Ubuntu 24.04 (agentforge-tester1 VM).

## Prerequisites Missing

| Step | Issue | Fix |
|------|-------|-----|
| 0 | curl not installed | `sudo apt install curl` |
| 1 | pip not installed | `sudo apt install python3-pip` |
| 2 | venv not available | `sudo apt install python3.12-venv` |
| 3 | "externally-managed-environment" | Must use venv (can't pip install globally) |

## One-Step Install Script (TODO)

```bash
#!/bin/bash
# agentforge-install.sh

set -e

echo "⚒️  Installing AgentForge..."

# Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3.12-venv git

# Clone repo
git clone https://github.com/Jakebot-ops/agentforge.git ~/.agentforge-install
cd ~/.agentforge-install

# Create venv and install
python3 -m venv venv
source venv/bin/activate
pip install -e .

# Add to PATH (optional)
echo 'alias agentforge="~/.agentforge-install/venv/bin/agentforge"' >> ~/.bashrc

echo "✅ AgentForge installed!"
echo "Run: source ~/.bashrc && agentforge --help"
```

## Testing Checklist

- [x] Clone repo
- [ ] pip install -e .
- [ ] agentforge --help
- [ ] agentforge init
- [ ] agentforge doctor
- [ ] agentforge start
- [ ] Dashboard accessible at localhost:7842

## Notes

- Ubuntu 24.04 uses Python 3.12
- PEP 668 enforces "externally-managed-environment" — venv is mandatory
- Consider using pipx for CLI tool installs in the future
