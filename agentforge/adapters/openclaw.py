"""OpenClaw platform adapter."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .base import BaseAdapter


class OpenClawAdapter(BaseAdapter):
    """Adapter for the OpenClaw agent platform."""
    
    name: str = "openclaw"
    
    def __init__(self):
        self.config_path = Path.home() / ".openclaw" / "openclaw.json"
        self.workspace_path = Path.home() / ".openclaw" / "workspace"
    
    def detect(self) -> bool:
        """Detect if OpenClaw is installed."""
        return self.config_path.exists()
    
    def get_workspace(self) -> Optional[Path]:
        """Get OpenClaw workspace directory."""
        if self.workspace_path.exists():
            return self.workspace_path
        return None
    
    def get_config(self) -> Dict[str, Any]:
        """Get OpenClaw configuration."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}
    
    def inject_memory(self, memory_path: Path) -> bool:
        """Inject memory system into OpenClaw workspace."""
        # Memory is already in workspace for OpenClaw
        target = self.workspace_path / "vector_memory"
        if memory_path == target or memory_path.exists():
            return True
        # Could create symlink or copy here
        return False
    
    def inject_healthkit(self, healthkit_path: Path) -> bool:
        """Inject healthkit into OpenClaw workspace."""
        # Healthkit is already in workspace for OpenClaw
        target = self.workspace_path / "healthkit_internal"
        if healthkit_path == target or healthkit_path.exists():
            return True
        return False
