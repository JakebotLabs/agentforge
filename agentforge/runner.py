"""Service runner for AgentForge."""

import subprocess
from pathlib import Path
from .config import AgentForgeConfig
from .platform import get_venv_python, kill_process, check_process_exists, popen_detached

PIDFILE_DIR = Path.home() / ".agentforge" / "pids"


def start_services(config: AgentForgeConfig, dashboard: bool = True, healthkit: bool = True) -> dict:
    """Start AgentForge services."""
    PIDFILE_DIR.mkdir(parents=True, exist_ok=True)
    results = {}

    # Start dashboard
    if dashboard and config.dashboard.enabled:
        dashboard_path = config.workspace / "jakebot-dashboard"
        if dashboard_path.exists():
            venv_python = get_venv_python(dashboard_path)
            if venv_python.exists():
                proc = popen_detached(
                    [str(venv_python), "-m", "uvicorn", "backend.main:app",
                     "--host", config.dashboard.host,
                     "--port", str(config.dashboard.port)],
                    cwd=dashboard_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                (PIDFILE_DIR / "dashboard.pid").write_text(str(proc.pid))
                results["dashboard"] = {"running": True, "message": f"Started on port {config.dashboard.port}", "pid": proc.pid}
            else:
                results["dashboard"] = {"running": False, "message": "venv not found. Run: cd jakebot-dashboard && python -m venv venv && pip install -e ."}
        else:
            results["dashboard"] = {"running": False, "message": "Dashboard not installed"}

    # Memory is passive (no service to start), just verify it exists
    if config.memory.enabled:
        memory_ok = (config.memory.path / "chroma_db").exists()
        results["memory"] = {"running": memory_ok, "message": "Ready" if memory_ok else "ChromaDB not found"}

    # HealthKit runs via cron/systemd, just verify it's configured
    if healthkit and config.healthkit.enabled:
        healthkit_ok = (config.healthkit.path / "monitor.py").exists()
        results["healthkit"] = {"running": healthkit_ok, "message": f"Mode: {config.healthkit.mode}" if healthkit_ok else "Not installed"}

    return results


def stop_services(config: AgentForgeConfig):
    """Stop all AgentForge services."""
    # Stop dashboard
    pidfile = PIDFILE_DIR / "dashboard.pid"
    if pidfile.exists():
        try:
            pid = int(pidfile.read_text().strip())
            kill_process(pid)
            pidfile.unlink()
        except (ProcessLookupError, ValueError):
            pidfile.unlink()


def get_status(config: AgentForgeConfig) -> dict:
    """Get status of all components."""
    status = {}

    # Dashboard
    pidfile = PIDFILE_DIR / "dashboard.pid"
    if pidfile.exists():
        try:
            pid = int(pidfile.read_text().strip())
            if check_process_exists(pid):
                status["Dashboard"] = {"healthy": True, "status": "Running", "details": f"PID {pid}, port {config.dashboard.port}"}
            else:
                status["Dashboard"] = {"healthy": False, "status": "Stopped", "details": ""}
                pidfile.unlink()
        except ValueError:
            status["Dashboard"] = {"healthy": False, "status": "Stopped", "details": ""}
            pidfile.unlink()
    else:
        status["Dashboard"] = {"healthy": False, "status": "Stopped", "details": ""}

    # Memory
    chroma_path = config.memory.path / "chroma_db"
    if chroma_path.exists():
        # Try to get chunk count
        try:
            import chromadb
            client = chromadb.PersistentClient(path=str(chroma_path))
            collections = client.list_collections()
            count = collections[0].count() if collections else 0
            status["Memory"] = {"healthy": True, "status": "Ready", "details": f"{count} chunks indexed"}
        except Exception:
            status["Memory"] = {"healthy": True, "status": "Ready", "details": "ChromaDB found"}
    else:
        status["Memory"] = {"healthy": False, "status": "Not initialized", "details": "Run indexer"}

    # HealthKit
    if (config.healthkit.path / "monitor.py").exists():
        status["HealthKit"] = {"healthy": True, "status": config.healthkit.mode.title(), "details": str(config.healthkit.path)}
    else:
        status["HealthKit"] = {"healthy": False, "status": "Not installed", "details": ""}

    # Pipeline
    from .components.pipeline import get_pipeline_status
    pipeline_status = get_pipeline_status(config.workspace)
    status["Pipeline"] = pipeline_status

    return status
