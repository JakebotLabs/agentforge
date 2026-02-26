"""Abstract base adapter for platform integrations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional


class BaseAdapter(ABC):
    """Abstract base class for platform adapters."""
    
    name: str = "base"
    
    @abstractmethod
    def detect(self) -> bool:
        """Detect if this platform is available."""
        pass
    
    @abstractmethod
    def get_workspace(self) -> Optional[Path]:
        """Get the platform's workspace directory."""
        pass
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration."""
        pass
    
    @abstractmethod
    def inject_memory(self, memory_path: Path) -> bool:
        """Inject memory system into the platform."""
        pass
    
    @abstractmethod
    def inject_healthkit(self, healthkit_path: Path) -> bool:
        """Inject healthkit into the platform."""
        pass
