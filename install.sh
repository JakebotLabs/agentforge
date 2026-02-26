#!/bin/bash
# AgentForge Installer
# Usage: curl -fsSL https://agentsforge.dev/install.sh | bash
#
# Options (env vars):
#   AGENTFORGE_HOME   Install path (default: ~/.agentforge)
#   AGENTFORGE_QUIET  Set to 1 to suppress output

set -euo pipefail

AGENTFORGE_HOME="${AGENTFORGE_HOME:-$HOME/.agentforge}"
REPO_URL="https://github.com/Jakebot-ops/agentforge.git"
MIN_PYTHON_MINOR=10   # Python 3.10+ required

# ── Colors ────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'
ok()   { echo -e "  ${GREEN}✅${RESET} $1"; }
warn() { echo -e "  ${YELLOW}⚠️ ${RESET} $1"; }
fail() { echo -e "  ${RED}❌${RESET} $1"; exit 1; }
info() { echo -e "  ${BLUE}→${RESET}  $1"; }

echo ""
echo -e "${BOLD}⚒️  AgentForge Installer${RESET}"
echo "════════════════════════════════════════"
echo ""

# ── 1. Python version check ───────────────────────────────────
echo "🔍 Checking prerequisites..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" -c "import sys; print(sys.version_info.minor)" 2>/dev/null || echo "0")
        major=$("$cmd" -c "import sys; print(sys.version_info.major)" 2>/dev/null || echo "0")
        if [[ "$major" -eq 3 && "$version" -ge "$MIN_PYTHON_MINOR" ]]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [[ -z "$PYTHON" ]]; then
    warn "Python 3.${MIN_PYTHON_MINOR}+ not found. Attempting to install..."
    if command -v apt-get &>/dev/null; then
        # Try deadsnakes PPA for modern Python without sudo risk
        if command -v sudo &>/dev/null && sudo -n true 2>/dev/null; then
            sudo apt-get update -qq
            sudo apt-get install -y -qq python3.12 python3.12-venv python3-pip git
            PYTHON="python3.12"
        else
            fail "Python 3.${MIN_PYTHON_MINOR}+ is required but not installed.\nPlease run: sudo apt-get install python3.12 python3.12-venv python3-pip git\nThen re-run this installer."
        fi
    elif command -v brew &>/dev/null; then
        brew install python@3.12 git 2>/dev/null || true
        PYTHON="python3"
    else
        fail "Python 3.${MIN_PYTHON_MINOR}+ is required. Please install it and re-run."
    fi
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1)
ok "Python: $PYTHON_VERSION"

# Check git
if ! command -v git &>/dev/null; then
    if command -v apt-get &>/dev/null && command -v sudo &>/dev/null && sudo -n true 2>/dev/null; then
        sudo apt-get install -y -qq git
    else
        fail "git is required. Please install it and re-run.\n  Ubuntu: sudo apt-get install git\n  macOS:  brew install git"
    fi
fi
ok "git: $(git --version)"

# ── 2. Detect platform ────────────────────────────────────────
echo ""
echo "🔍 Detecting platform..."

PLATFORM="standalone"
if command -v openclaw &>/dev/null && [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
    PLATFORM="openclaw"
    ok "OpenClaw detected — using openclaw platform"
elif python3 -c "import langchain" &>/dev/null 2>&1; then
    PLATFORM="langchain"
    ok "LangChain detected"
else
    ok "Platform: standalone"
fi

# ── 3. Install ────────────────────────────────────────────────
echo ""
echo "📥 Installing AgentForge..."
mkdir -p "$AGENTFORGE_HOME"

# Clone or update
if [[ -d "$AGENTFORGE_HOME/repo/.git" ]]; then
    info "Updating existing installation..."
    git -C "$AGENTFORGE_HOME/repo" fetch -q origin
    git -C "$AGENTFORGE_HOME/repo" reset -q --hard origin/main
else
    info "Cloning repository..."
    git clone -q "$REPO_URL" "$AGENTFORGE_HOME/repo"
    # Ensure latest (CDN cache can serve stale clone)
    git -C "$AGENTFORGE_HOME/repo" fetch -q origin
    git -C "$AGENTFORGE_HOME/repo" reset -q --hard origin/main
fi
ok "Repository ready ($(git -C "$AGENTFORGE_HOME/repo" rev-parse --short HEAD))"

# Python venv
info "Setting up Python environment..."
if [[ ! -d "$AGENTFORGE_HOME/venv" ]]; then
    "$PYTHON" -m venv "$AGENTFORGE_HOME/venv"
fi

"$AGENTFORGE_HOME/venv/bin/pip" install -q --upgrade pip
"$AGENTFORGE_HOME/venv/bin/pip" install -q "$AGENTFORGE_HOME/repo"
ok "Python environment ready"

# ── 4. Add to PATH (not alias) ────────────────────────────────
info "Installing agentforge command..."
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

cat > "$LOCAL_BIN/agentforge" << WRAPPER
#!/bin/bash
exec "$AGENTFORGE_HOME/venv/bin/agentforge" "\$@"
WRAPPER
chmod +x "$LOCAL_BIN/agentforge"

# Ensure ~/.local/bin is in PATH (add to shell rc if missing)
for RC in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
    [[ -f "$RC" ]] || continue
    if ! grep -q 'HOME/.local/bin' "$RC" 2>/dev/null; then
        echo '' >> "$RC"
        echo '# AgentForge / local binaries' >> "$RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$RC"
    fi
done

ok "Command installed: $LOCAL_BIN/agentforge"

# Make it available in current shell without restart
export PATH="$LOCAL_BIN:$PATH"

# ── 5. Initialize ─────────────────────────────────────────────
echo ""
"$LOCAL_BIN/agentforge" init --platform "$PLATFORM" --no-install

# ── 6. Verify ─────────────────────────────────────────────────
echo ""
echo "🩺 Running diagnostics..."
"$LOCAL_BIN/agentforge" doctor

# ── 7. Done ───────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}${BOLD}✅ AgentForge installed successfully!${RESET}"
echo ""
echo "Platform: $PLATFORM"
echo "Location: $AGENTFORGE_HOME"
echo ""
echo -e "${BOLD}Get started:${RESET}"
echo "  agentforge status    # see what's running"
echo "  agentforge start     # launch all services"
echo "  agentforge doctor    # diagnose issues"
echo ""
echo -e "${YELLOW}Note:${RESET} Open a new terminal (or run: export PATH=\"\$HOME/.local/bin:\$PATH\")"
echo "      if 'agentforge' command isn't found yet."
echo ""
echo "Docs: https://agentsforge.dev"
echo "════════════════════════════════════════"
echo ""
