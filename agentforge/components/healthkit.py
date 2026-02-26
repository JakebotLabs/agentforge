"""Agent HealthKit component."""

from pathlib import Path
from typing import Any, Dict


class HealthkitComponent:
    """Manages the agent healthkit monitoring system."""
    
    name: str = "agent-healthkit"
    
    def __init__(self, path: Path, mode: str = "observe"):
        self.path = path
        self.mode = mode  # observe | heal
        self.monitor_path = path / "monitor.py"
    
    def is_installed(self) -> bool:
        """Check if healthkit is installed."""
        return self.path.exists() and self.monitor_path.exists()
    
    def get_status(self) -> Dict[str, Any]:
        """Get healthkit status."""
        return {
            "installed": self.is_installed(),
            "path": str(self.path),
            "mode": self.mode,
            "monitor_exists": self.monitor_path.exists(),
        }
    
    def run_check(self) -> Dict[str, Any]:
        """Run a health check."""
        if not self.is_installed():
            return {"error": "HealthKit not installed"}
        
        # Import and run the monitor
        try:
            import subprocess
            import sys
            
            result = subprocess.run(
                [sys.executable, str(self.monitor_path), "--check"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
        except Exception as e:
            return {"error": str(e)}
