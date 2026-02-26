"""Component installation logic for AgentForge."""

from pathlib import Path
import subprocess
import sys
from .config import AgentForgeConfig


def install_components(config: AgentForgeConfig) -> dict:
    """Check and install AgentForge components."""
    results = {}
    
    # Check memory system
    memory_path = config.memory.path
    if memory_path.exists() and (memory_path / "chroma_db").exists():
        results["persistent-memory"] = {"installed": True, "message": f"Found at {memory_path}"}
    else:
        results["persistent-memory"] = {"installed": False, "message": "Not found. Run setup."}
    
    # Check healthkit
    healthkit_path = config.healthkit.path
    if healthkit_path.exists() and (healthkit_path / "monitor.py").exists():
        results["agent-healthkit"] = {"installed": True, "message": f"Found at {healthkit_path}"}
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
        local_dashboard = config.workspace / "jakebot-dashboard"
        if local_dashboard.exists():
            results["dashboard"] = {"installed": True, "message": f"Found at {local_dashboard}"}
        else:
            results["dashboard"] = {"installed": False, "message": "Not found."}
    
    return results


def check_components(config: AgentForgeConfig) -> dict:
    """Run diagnostic checks on all components."""
    checks = {}
    
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
    dashboard_path = config.workspace / "jakebot-dashboard"
    checks["Dashboard"] = {
        "ok": dashboard_path.exists(),
        "message": "Found" if dashboard_path.exists() else "Not found",
        "fix": "Clone jakebot-dashboard repo"
    }
    
    # Python version
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    checks["Python version"] = {
        "ok": py_ok,
        "message": f"{py_version.major}.{py_version.minor}.{py_version.micro}",
        "fix": "Requires Python 3.10+"
    }
    
    return checks
