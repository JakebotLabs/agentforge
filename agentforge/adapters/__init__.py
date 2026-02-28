"""Platform adapters for AgentForge."""

from .base import BaseAdapter
from .openclaw import OpenClawAdapter
from .langchain import LangChainAdapter
from .autogen import AutoGenAdapter
from .standalone import StandaloneAdapter

__all__ = [
    "BaseAdapter",
    "OpenClawAdapter",
    "LangChainAdapter",
    "AutoGenAdapter",
    "StandaloneAdapter",
]
