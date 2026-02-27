#!/bin/bash
# AgentForge Installer
# Usage: curl -fsSL https://agentsforge.dev/install.sh | bash
#
# Options (env vars):
#   AGENTFORGE_HOME   Install path (default: ~/.agentforge)
#   AGENTFORGE_QUIET  Set to 1 to suppress output
#
# Flags:
#   --mailbox         Also clone agent-mailbox for multi-agent coordination
#   --upgrade         Force upgrade existing installation
#   --help            Show this help

set -euo pipefail

AGENTFORGE_HOME="${AGENTFORGE_HOME:-$HOME/.agentforge}"
REPO_URL="https://github.com/JakebotLabs/agentforge.git"
MAILBOX_URL="https://github.com/JakebotLabs/agent-mailbox.git"
MAILBOX_PATH="$HOME/.openclaw/mailbox"
MIN_PYTHON_MINOR=10   # Python 3.10+ required

# Parse flags
INSTALL_MAILBOX=false
FORCE_UPGRADE=false
for arg in "$@"; do
    case "$arg" in
        --mailbox)   INSTALL_MAILBOX=true ;;
        --upgrade)   FORCE_UPGRADE=true ;;
        --help|-h)
            echo "AgentForge Installer"
            echo ""
            echo "Usage: curl -fsSL https://agentsforge.dev/install.sh | bash [-s -- OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --mailbox   Also install agent-mailbox for multi-agent coordination"
            echo "  --upgrade   Force upgrade existing installation"
            echo "  --help      Show this help"
            echo ""
            echo "Environment variables:"
            echo "  AGENTFORGE_HOME   Install path (default: ~/.agentforge)"
            exit 0
            ;;
    esac
done

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

# ── 1. Dependency checks ──────────────────────────────────────
echo "🔍 Checking prerequisites..."

# Check git first (needed for everything)
if ! command -v git &>/dev/null; then
    fail "git is required but not installed.\n\n  Ubuntu/Debian: sudo apt-get install git\n  macOS:         brew install git\n  Windows:       https://git-scm.com/download/win\n\nPlease install git and re-run this installer."
fi
ok "git: $(git --version)"

# Check Python version
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
    # Check if any python exists but wrong version
    if command -v python3 &>/dev/null; then
        CURRENT_VER=$(python3 --version 2>&1)
        fail "Python 3.${MIN_PYTHON_MINOR}+ required, but found: $CURRENT_VER\n\n  Ubuntu/Debian: sudo apt-get install python3.12 python3.12-venv\n  macOS:         brew install python@3.12\n  Windows:       https://python.org/downloads/\n\nPlease upgrade Python and re-run."
    else
        fail "Python 3.${MIN_PYTHON_MINOR}+ is required but not installed.\n\n  Ubuntu/Debian: sudo apt-get install python3.12 python3.12-venv python3-pip\n  macOS:         brew install python@3.12\n  Windows:       https://python.org/downloads/\n\nPlease install Python and re-run."
    fi
fi

PYTHON_VERSION=$("$PYTHON" --version 2>&1)
ok "Python: $PYTHON_VERSION"

# Check pip/venv availability
if ! "$PYTHON" -m pip --version &>/dev/null; then
    fail "pip module not found for $PYTHON.\n\n  Ubuntu/Debian: sudo apt-get install python3-pip\n  Other: $PYTHON -m ensurepip"
fi

if ! "$PYTHON" -c "import venv" &>/dev/null; then
    fail "venv module not found for $PYTHON.\n\n  Ubuntu/Debian: sudo apt-get install python3.12-venv\n  Other: Install the python-venv package for your Python version"
fi

ok "pip + venv modules available"

# ── 2. Handle existing installation ───────────────────────────
if [[ -d "$AGENTFORGE_HOME/repo/.git" ]]; then
    echo ""
    if [[ "$FORCE_UPGRADE" == "true" ]]; then
        info "Upgrading existing installation (--upgrade flag)..."
    else
        echo -e "${YELLOW}Existing installation detected at $AGENTFORGE_HOME${RESET}"
        echo ""
        echo "  [1] Upgrade — pull latest changes and update"
        echo "  [2] Fresh   — remove and reinstall from scratch"
        echo "  [3] Cancel  — exit without changes"
        echo ""
        read -rp "  Choice [1]: " choice
        choice="${choice:-1}"
        
        case "$choice" in
            1)
                info "Upgrading existing installation..."
                ;;
            2)
                warn "Removing existing installation..."
                rm -rf "$AGENTFORGE_HOME"
                ;;
            3)
                echo "Cancelled."
                exit 0
                ;;
            *)
                fail "Invalid choice. Run again and select 1, 2, or 3."
                ;;
        esac
    fi
fi

# ── 3. Detect platform ────────────────────────────────────────
echo ""
echo "🔍 Detecting platform..."

PLATFORM="standalone"
if command -v openclaw &>/dev/null && [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
    PLATFORM="openclaw"
    ok "OpenClaw detected — using openclaw platform"
elif "$PYTHON" -c "import langchain" &>/dev/null 2>&1; then
    PLATFORM="langchain"
    ok "LangChain detected"
else
    ok "Platform: standalone"
fi

# ── 4. Install AgentForge ─────────────────────────────────────
echo ""
echo "📥 Installing AgentForge..."
mkdir -p "$AGENTFORGE_HOME"

# Clone or update
if [[ -d "$AGENTFORGE_HOME/repo/.git" ]]; then
    info "Updating existing repository..."
    git -C "$AGENTFORGE_HOME/repo" fetch -q origin
    git -C "$AGENTFORGE_HOME/repo" reset -q --hard origin/main
else
    info "Cloning repository..."
    if ! git clone -q "$REPO_URL" "$AGENTFORGE_HOME/repo" 2>&1; then
        fail "Failed to clone repository. Check your internet connection and try again."
    fi
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

# ── 5. Add to PATH (not alias) ────────────────────────────────
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

# ── 6. Verify installation ────────────────────────────────────
echo ""
echo "🔍 Verifying installation..."

if ! "$LOCAL_BIN/agentforge" --version &>/dev/null; then
    fail "agentforge command failed to run. Installation may be corrupted.\n\nTry: rm -rf $AGENTFORGE_HOME && re-run installer"
fi

INSTALLED_VERSION=$("$LOCAL_BIN/agentforge" --version 2>&1 || echo "unknown")
ok "agentforge $INSTALLED_VERSION"

# ── 7. Initialize ─────────────────────────────────────────────
echo ""
"$LOCAL_BIN/agentforge" init --platform "$PLATFORM" --no-install

# ── 8. Install Agent Mailbox (optional) ───────────────────────
if [[ "$INSTALL_MAILBOX" == "true" ]]; then
    echo ""
    echo "📬 Installing Agent Mailbox..."
    
    mkdir -p "$(dirname "$MAILBOX_PATH")"
    
    if [[ -d "$MAILBOX_PATH/.git" ]]; then
        info "Updating existing mailbox..."
        git -C "$MAILBOX_PATH" pull -q origin main || warn "Failed to update mailbox (continuing anyway)"
    else
        info "Cloning agent-mailbox..."
        if git clone -q "$MAILBOX_URL" "$MAILBOX_PATH" 2>&1; then
            ok "Agent Mailbox installed at $MAILBOX_PATH"
        else
            warn "Failed to clone agent-mailbox (may be private repo)"
            warn "Get access at: github.com/JakebotLabs/agent-mailbox"
        fi
    fi
fi

# ── 9. Run diagnostics ────────────────────────────────────────
echo ""
echo "🩺 Running diagnostics..."
"$LOCAL_BIN/agentforge" doctor

# ── 10. Done ──────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════"
echo -e "${GREEN}${BOLD}✅ AgentForge installed successfully!${RESET}"
echo ""
echo "Platform: $PLATFORM"
echo "Location: $AGENTFORGE_HOME"
echo "Version:  $INSTALLED_VERSION"
echo ""
echo -e "${BOLD}Get started:${RESET}"
echo "  agentforge status    # see what's running"
echo "  agentforge start     # launch all services"
echo "  agentforge doctor    # diagnose issues"
echo ""
if [[ "$INSTALL_MAILBOX" == "true" && -d "$MAILBOX_PATH" ]]; then
    echo -e "${BOLD}Agent Mailbox:${RESET}"
    echo "  cd $MAILBOX_PATH"
    echo "  python mailbox.py --agent <your-id> onboard"
    echo ""
fi
echo -e "${YELLOW}Note:${RESET} Open a new terminal (or run: export PATH=\"\$HOME/.local/bin:\$PATH\")"
echo "      if 'agentforge' command isn't found yet."
echo ""
echo "Docs: https://agentsforge.dev"
echo "════════════════════════════════════════"
echo ""
