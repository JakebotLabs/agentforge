"""Component installation logic for AgentForge."""

from pathlib import Path
import subprocess
import sys
from .config import AgentForgeConfig
from .platform import get_venv_pip


def install_all_components(config: AgentForgeConfig, console) -> dict:
    """Clone and set up all AgentForge components."""
    results = {}
    components_dir = Path(config.workspace) / "components"
    components_dir.mkdir(parents=True, exist_ok=True)
    
    REPOS = {
        "agent-memory-core": ("https://github.com/JakebotLabs/agent-memory-core.git", False),
        "agent-healthkit": ("https://github.com/JakebotLabs/agent-healthkit.git", False),
        "agent-mailbox": ("https://github.com/JakebotLabs/agent-mailbox.git", False),
        "jakebot-dashboard": ("https://github.com/JakebotLabs/jakebot-dashboard.git", False),
        "pipeline": ("https://github.com/JakebotLabs/agentforge-pipeline.git", True),  # Pro feature
    }
    
    for name, (url, is_pro) in REPOS.items():
        target = components_dir / name
        
        if is_pro:
            console.print(f"  🔐 [cyan]{name}[/] (Pro feature)...")
        else:
            console.print(f"  📦 Installing {name}...")
        
        if target.exists():
            # Update existing
            result = subprocess.run(["git", "-C", str(target), "pull"], 
                                  capture_output=True, text=True)
            results[name] = {"installed": True, "message": "Updated", "pro": is_pro}
        else:
            # Clone new
            result = subprocess.run(["git", "clone", url, str(target)],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                results[name] = {"installed": True, "message": "Cloned", "pro": is_pro}
            elif is_pro and ("Authentication failed" in result.stderr or "could not read" in result.stderr.lower()):
                # Pro feature - user doesn't have access
                results[name] = {
                    "installed": False, 
                    "message": "🔒 Pro feature — sponsor at github.com/sponsors/JakebotLabs",
                    "pro": True,
                    "locked": True
                }
            else:
                results[name] = {"installed": False, "message": result.stderr[:100], "pro": is_pro}
        
        # Set up Python venv for each component if requirements.txt exists
        req_file = target / "requirements.txt"
        if req_file.exists():
            venv_path = target / "venv"
            if not venv_path.exists():
                subprocess.run([sys.executable, "-m", "venv", str(venv_path)],
                             capture_output=True)
            pip = get_venv_pip(target)
            subprocess.run([str(pip), "install", "-q", "-r", str(req_file)],
                         capture_output=True)
            console.print(f"    ✅ {name} dependencies installed")
    
    return results


def install_components(config: AgentForgeConfig) -> dict:
    """Check and install AgentForge components."""
    results = {}
    
    # Check memory system
    memory_path = config.memory.path
    if memory_path.exists() and (memory_path / "chroma_db").exists():
        results["agent-memory-core"] = {"installed": True, "message": f"Found at {memory_path}"}
    else:
        results["agent-memory-core"] = {"installed": False, "message": "Not found. Run setup."}
    
    # Check healthkit
    healthkit_path = config.healthkit.path
    if healthkit_path.exists() and (healthkit_path / "monitor.py").exists():
        results["agent-healthkit"] = {"installed": True, "message": f"Found at {str(healthkit_path).strip()}"}
    else:
        results["agent-healthkit"] = {"installed": False, "message": "Not found."}
    
    # Check dashboard
    dashboard_installed = False
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "jakebot-dashboard"],
                              capture_output=True, text=True)
        dashboard_installed = result.returncode == 0
    except Exception:
        pass
    
    if dashboard_installed:
        results["dashboard"] = {"installed": True, "message": "Installed via pip"}
    else:
        # Check local install
        local_dashboard = Path(config.workspace) / "components" / "jakebot-dashboard"
        if local_dashboard.exists():
            results["dashboard"] = {"installed": True, "message": f"Found at {local_dashboard}"}
        else:
            results["dashboard"] = {"installed": False, "message": "Not found."}
    
    # Check dev pipeline (Pro feature)
    from .components.pipeline import check_pipeline
    pipeline_check = check_pipeline(config.workspace)
    if pipeline_check["installed"]:
        results["pipeline"] = {"installed": True, "message": f"Found at {pipeline_check['path']}"}
    else:
        results["pipeline"] = {
            "installed": None,  # Not an error — Pro feature
            "message": "Pro feature — github.com/sponsors/JakebotLabs",
        }
    
    return results


def check_components(config: AgentForgeConfig) -> dict:
    """Run diagnostic checks on all components."""
    import shutil
    import urllib.request
    import urllib.error
    
    checks = {}
    
    # Python version (check first - most important)
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    checks["Python version"] = {
        "ok": py_ok,
        "message": f"{py_version.major}.{py_version.minor}.{py_version.micro}",
        "fix": "Requires Python 3.10+ — https://python.org/downloads/"
    }
    
    # git available
    git_path = shutil.which("git")
    if git_path:
        try:
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
            git_version = result.stdout.strip() if result.returncode == 0 else "unknown"
            checks["git"] = {"ok": True, "message": git_version, "fix": None}
        except Exception:
            checks["git"] = {"ok": False, "message": "Error running git", "fix": "Reinstall git"}
    else:
        checks["git"] = {
            "ok": False,
            "message": "Not found in PATH",
            "fix": "Install git: apt-get install git (Linux) / brew install git (macOS)"
        }
    
    # npm available (optional, for @agentsforge/healthkit users)
    npm_path = shutil.which("npm")
    if npm_path:
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
            npm_version = result.stdout.strip() if result.returncode == 0 else "unknown"
            checks["npm"] = {"ok": True, "message": f"v{npm_version}", "fix": None}
        except Exception:
            checks["npm"] = {"ok": True, "message": "Found but version check failed", "fix": None}
    else:
        checks["npm"] = {
            "ok": True,  # Optional - not a failure
            "message": "Not found (optional — for @agentsforge/healthkit)",
            "fix": "Install Node.js: https://nodejs.org/"
        }
    
    # agentsforge.dev reachable
    try:
        req = urllib.request.Request(
            "https://agentsforge.dev",
            headers={"User-Agent": "AgentForge-Doctor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            checks["agentsforge.dev"] = {
                "ok": resp.status == 200,
                "message": "Reachable" if resp.status == 200 else f"HTTP {resp.status}",
                "fix": None
            }
    except urllib.error.URLError as e:
        checks["agentsforge.dev"] = {
            "ok": False,
            "message": f"Unreachable: {e.reason}",
            "fix": "Check internet connection or firewall"
        }
    except Exception as e:
        checks["agentsforge.dev"] = {
            "ok": False,
            "message": f"Error: {str(e)[:50]}",
            "fix": "Check internet connection"
        }
    
    # Agent Mailbox (optional but recommended for multi-agent)
    mailbox_path = Path.home() / ".openclaw" / "mailbox"
    if mailbox_path.exists() and (mailbox_path / ".git").exists():
        checks["Agent Mailbox"] = {
            "ok": True,
            "message": f"Found at {mailbox_path}",
            "fix": None
        }
    else:
        checks["Agent Mailbox"] = {
            "ok": True,  # Optional - not a failure
            "message": "Not installed (optional — for multi-agent coordination)",
            "fix": "git clone https://github.com/JakebotLabs/agent-mailbox.git ~/.openclaw/mailbox"
        }
    
    # Config file exists
    from .config import DEFAULT_CONFIG_PATH
    checks["Config file"] = {
        "ok": DEFAULT_CONFIG_PATH.exists(),
        "message": str(DEFAULT_CONFIG_PATH) if DEFAULT_CONFIG_PATH.exists() else "Missing",
        "fix": "Run: agentforge init"
    }
    
    # Memory system
    memory_path = config.memory.path
    chroma_exists = (memory_path / "chroma_db").exists()
    checks["Memory (ChromaDB)"] = {
        "ok": chroma_exists,
        "message": "Database found" if chroma_exists else "No ChromaDB",
        "fix": "Run the memory indexer"
    }
    
    # Healthkit
    healthkit_path = config.healthkit.path
    monitor_exists = (healthkit_path / "monitor.py").exists()
    checks["HealthKit"] = {
        "ok": monitor_exists,
        "message": "Monitor found" if monitor_exists else "Not installed",
        "fix": "Install agent-healthkit"
    }
    
    # Dashboard
    dashboard_path = Path(config.workspace) / "components" / "jakebot-dashboard"
    checks["Dashboard"] = {
        "ok": dashboard_path.exists(),
        "message": "Found" if dashboard_path.exists() else "Not found",
        "fix": "Clone jakebot-dashboard repo"
    }
    
    # Pipeline
    from .components.pipeline import check_pipeline
    pipeline_check = check_pipeline(config.workspace)
    checks["Pipeline"] = {
        "ok": True,   # Not having Pro is not a failure
        "message": "CodeBot + OpusBot ready" if pipeline_check["installed"] else "🔒 Pro feature (optional)",
        "fix": None
    }

    # OpenClaw platform check (only when platform=openclaw)
    openclaw_cmd = shutil.which("openclaw")
    openclaw_json = Path.home() / ".openclaw" / "openclaw.json"

    if config.platform == "openclaw" or openclaw_cmd:
        # 1. openclaw command exists
        if not openclaw_cmd:
            checks["OpenClaw CLI"] = {
                "ok": False,
                "message": "openclaw command not found",
                "fix": "Install OpenClaw: npm install -g openclaw"
            }
        else:
            try:
                result = subprocess.run(["openclaw", "--version"], capture_output=True, text=True, timeout=5)
                oc_version = result.stdout.strip() or result.stderr.strip() or "installed"
                checks["OpenClaw CLI"] = {
                    "ok": True,
                    "message": oc_version,
                    "fix": None
                }
            except Exception:
                checks["OpenClaw CLI"] = {
                    "ok": True,
                    "message": "Found (version check failed)",
                    "fix": None
                }

        # 2. ~/.openclaw/openclaw.json exists
        if not openclaw_json.exists():
            checks["OpenClaw config"] = {
                "ok": False,
                "message": f"{openclaw_json} not found",
                "fix": "Run: openclaw configure  (or: openclaw configure --section model)"
            }
        else:
            # 3. agents.defaults.model.primary is set
            try:
                import json as _json
                with open(openclaw_json) as _f:
                    _oc_cfg = _json.load(_f)

                _primary = (
                    _oc_cfg
                    .get("agents", {})
                    .get("defaults", {})
                    .get("model", {})
                    .get("primary", "")
                )

                if _primary:
                    checks["OpenClaw config"] = {
                        "ok": True,
                        "message": f"Model configured: {_primary}",
                        "fix": None
                    }
                else:
                    checks["OpenClaw config"] = {
                        "ok": False,
                        "message": "No primary model set (agents.defaults.model.primary is empty)",
                        "fix": "Run: openclaw configure --section model  — then pick your AI provider/model"
                    }
            except Exception as e:
                checks["OpenClaw config"] = {
                    "ok": False,
                    "message": f"Could not parse openclaw.json: {str(e)[:60]}",
                    "fix": "Run: openclaw configure --section model"
                }

    return checks
