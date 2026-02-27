"""Dashboard component."""

import subprocess
from pathlib import Path
from typing import Any, Dict

from ..platform import get_venv_python, kill_process, check_process_exists, popen_detached


class DashboardComponent:
    """Manages the Jakebot dashboard web UI."""

    name: str = "dashboard"

    def __init__(self, path: Path, host: str = "127.0.0.1", port: int = 7842):
        self.path = path
        self.host = host
        self.port = port
        self.venv_python = get_venv_python(path)
        self.pidfile = Path.home() / ".agentforge" / "pids" / "dashboard.pid"

    def is_installed(self) -> bool:
        """Check if dashboard is installed."""
        return self.path.exists() and (self.path / "backend").exists()

    def is_running(self) -> bool:
        """Check if dashboard is currently running."""
        if not self.pidfile.exists():
            return False

        try:
            pid = int(self.pidfile.read_text().strip())
            if check_process_exists(pid):
                return True
            self.pidfile.unlink(missing_ok=True)
            return False
        except ValueError:
            self.pidfile.unlink(missing_ok=True)
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get dashboard status."""
        running = self.is_running()
        pid = None
        if running and self.pidfile.exists():
            pid = int(self.pidfile.read_text().strip())

        return {
            "installed": self.is_installed(),
            "running": running,
            "path": str(self.path),
            "url": f"http://{self.host}:{self.port}" if running else None,
            "pid": pid,
        }

    def start(self) -> Dict[str, Any]:
        """Start the dashboard."""
        if not self.is_installed():
            return {"success": False, "error": "Dashboard not installed"}

        if self.is_running():
            return {"success": True, "message": "Already running"}

        if not self.venv_python.exists():
            return {"success": False, "error": "venv not found"}

        self.pidfile.parent.mkdir(parents=True, exist_ok=True)

        proc = popen_detached(
            [str(self.venv_python), "-m", "uvicorn", "backend.main:app",
             "--host", self.host, "--port", str(self.port)],
            cwd=self.path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        self.pidfile.write_text(str(proc.pid))

        return {
            "success": True,
            "pid": proc.pid,
            "url": f"http://{self.host}:{self.port}"
        }

    def stop(self) -> Dict[str, Any]:
        """Stop the dashboard."""
        if not self.is_running():
            return {"success": True, "message": "Not running"}

        try:
            pid = int(self.pidfile.read_text().strip())
            kill_process(pid)
            self.pidfile.unlink(missing_ok=True)
            return {"success": True, "message": f"Stopped PID {pid}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
