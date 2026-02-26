"""Platform adapters for AgentForge."""

from .base import BaseAdapter
from .openclaw import OpenClawAdapter

__all__ = ["BaseAdapter", "OpenClawAdapter"]
