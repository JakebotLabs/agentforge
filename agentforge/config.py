"""Configuration management for AgentForge."""

from pathlib import Path
from typing import Union
from pydantic import BaseModel, field_serializer
import yaml

DEFAULT_CONFIG_PATH = Path.home() / ".agentforge" / "agentforge.yml"


class MemoryConfig(BaseModel):
    enabled: bool = True
    path: Path = Path.home() / ".openclaw/workspace/vector_memory"

    @field_serializer('path')
    def serialize_path(self, path: Path) -> str:
        return str(path)


class HealthkitConfig(BaseModel):
    enabled: bool = True
    path: Path = Path.home() / ".openclaw/workspace/healthkit_internal"
    mode: str = "observe"  # observe | heal

    @field_serializer('path')
    def serialize_path(self, path: Path) -> str:
        return str(path)


class DashboardConfig(BaseModel):
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 7842


class AgentForgeConfig(BaseModel):
    version: str = "1"
    platform: str = "openclaw"  # openclaw | langchain | standalone
    workspace: Path = Path.home() / ".openclaw/workspace"
    memory: MemoryConfig = MemoryConfig()
    healthkit: HealthkitConfig = HealthkitConfig()
    dashboard: DashboardConfig = DashboardConfig()

    @field_serializer('workspace')
    def serialize_workspace(self, workspace: Path) -> str:
        return str(workspace)


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AgentForgeConfig:
    """Load configuration from YAML file."""
    if path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
        # Convert string paths back to Path objects for nested configs
        if 'memory' in data and 'path' in data['memory']:
            data['memory']['path'] = Path(data['memory']['path']).expanduser()
        if 'healthkit' in data and 'path' in data['healthkit']:
            data['healthkit']['path'] = Path(data['healthkit']['path']).expanduser()
        if 'workspace' in data:
            data['workspace'] = Path(data['workspace']).expanduser()
        return AgentForgeConfig(**data)
    return AgentForgeConfig()


def save_config(config: AgentForgeConfig, path: Path = DEFAULT_CONFIG_PATH):
    """Save configuration to YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        yaml.dump(config.model_dump(mode="json"), f, default_flow_style=False)
