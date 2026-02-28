"""Tests for platform adapters: LangChain, Standalone."""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest


# ---------------------------------------------------------------------------
# LangChain Adapter
# ---------------------------------------------------------------------------

class TestLangChainAdapter:
    def _adapter(self, tmp_path: Path):
        from agentforge.adapters.langchain import LangChainAdapter
        a = LangChainAdapter()
        a.workspace_path = tmp_path / "langchain"
        return a

    def test_detect_when_langchain_installed(self, tmp_path):
        adapter = self._adapter(tmp_path)
        import types
        fake_lc = types.ModuleType("langchain")
        with patch.dict(sys.modules, {"langchain": fake_lc}):
            assert adapter.detect() is True

    def test_detect_when_langchain_missing(self, tmp_path):
        adapter = self._adapter(tmp_path)
        with patch.dict(sys.modules, {"langchain": None}):
            # None in sys.modules raises ImportError on import
            assert adapter.detect() is False

    def test_get_workspace_creates_directory(self, tmp_path):
        adapter = self._adapter(tmp_path)
        ws = adapter.get_workspace()
        assert ws is not None
        assert ws.exists()

    def test_get_config_returns_platform_key(self, tmp_path):
        adapter = self._adapter(tmp_path)
        cfg = adapter.get_config()
        assert cfg["platform"] == "langchain"
        assert "workspace" in cfg

    def test_inject_memory_writes_bridge(self, tmp_path):
        adapter = self._adapter(tmp_path)
        memory_path = tmp_path / "vector_memory"
        memory_path.mkdir()
        result = adapter.inject_memory(memory_path)
        assert result is True
        bridge = adapter.workspace_path / "memory_bridge.py"
        assert bridge.exists()
        content = bridge.read_text()
        assert "MemoryStore" not in content  # LangChain bridge uses Chroma directly
        assert "Chroma" in content or "vector_store" in content

    def test_inject_memory_contains_correct_path(self, tmp_path):
        adapter = self._adapter(tmp_path)
        memory_path = tmp_path / "my_vector_memory"
        memory_path.mkdir()
        adapter.inject_memory(memory_path)
        content = (adapter.workspace_path / "memory_bridge.py").read_text()
        assert str(memory_path) in content

    def test_inject_healthkit_writes_callbacks(self, tmp_path):
        adapter = self._adapter(tmp_path)
        hk_path = tmp_path / "healthkit"
        hk_path.mkdir()
        result = adapter.inject_healthkit(hk_path)
        assert result is True
        cb = adapter.workspace_path / "healthkit_callbacks.py"
        assert cb.exists()
        content = cb.read_text()
        assert "HealthKitCallbackHandler" in content

    def test_inject_healthkit_contains_correct_path(self, tmp_path):
        adapter = self._adapter(tmp_path)
        hk_path = tmp_path / "my_healthkit"
        hk_path.mkdir()
        adapter.inject_healthkit(hk_path)
        content = (adapter.workspace_path / "healthkit_callbacks.py").read_text()
        assert str(hk_path) in content

    def test_write_example_creates_file(self, tmp_path):
        adapter = self._adapter(tmp_path)
        example = adapter.write_example()
        assert example.exists()
        content = example.read_text()
        assert "memory_bridge" in content
        assert "healthkit_callbacks" in content


# ---------------------------------------------------------------------------
# Standalone Adapter
# ---------------------------------------------------------------------------

class TestStandaloneAdapter:
    def _adapter(self, tmp_path: Path):
        from agentforge.adapters.standalone import StandaloneAdapter
        a = StandaloneAdapter()
        a.workspace_path = tmp_path / "standalone"
        return a

    def test_detect_always_true(self, tmp_path):
        adapter = self._adapter(tmp_path)
        assert adapter.detect() is True

    def test_get_workspace_creates_directory(self, tmp_path):
        adapter = self._adapter(tmp_path)
        ws = adapter.get_workspace()
        assert ws is not None
        assert ws.exists()

    def test_get_config_returns_platform_key(self, tmp_path):
        adapter = self._adapter(tmp_path)
        cfg = adapter.get_config()
        assert cfg["platform"] == "standalone"
        assert "workspace" in cfg

    def test_inject_memory_writes_setup(self, tmp_path):
        adapter = self._adapter(tmp_path)
        memory_path = tmp_path / "vector_memory"
        memory_path.mkdir()
        result = adapter.inject_memory(memory_path)
        assert result is True
        setup = adapter.workspace_path / "memory_setup.py"
        assert setup.exists()
        content = setup.read_text()
        assert "MemoryStore" in content

    def test_inject_memory_contains_correct_path(self, tmp_path):
        adapter = self._adapter(tmp_path)
        memory_path = tmp_path / "my_memory"
        memory_path.mkdir()
        adapter.inject_memory(memory_path)
        content = (adapter.workspace_path / "memory_setup.py").read_text()
        assert str(memory_path) in content

    def test_inject_healthkit_writes_setup(self, tmp_path):
        adapter = self._adapter(tmp_path)
        hk_path = tmp_path / "healthkit"
        hk_path.mkdir()
        result = adapter.inject_healthkit(hk_path)
        assert result is True
        setup = adapter.workspace_path / "healthkit_setup.py"
        assert setup.exists()
        content = setup.read_text()
        assert "HealthKit" in content

    def test_inject_healthkit_contains_correct_path(self, tmp_path):
        adapter = self._adapter(tmp_path)
        hk_path = tmp_path / "my_healthkit"
        hk_path.mkdir()
        adapter.inject_healthkit(hk_path)
        content = (adapter.workspace_path / "healthkit_setup.py").read_text()
        assert str(hk_path) in content

    def test_write_example_creates_file(self, tmp_path):
        adapter = self._adapter(tmp_path)
        example = adapter.write_example()
        assert example.exists()
        content = example.read_text()
        assert "MemoryStore" in content
        assert "HealthKit" in content

    def test_memory_setup_has_add_and_query(self, tmp_path):
        adapter = self._adapter(tmp_path)
        memory_path = tmp_path / "vector_memory"
        memory_path.mkdir()
        adapter.inject_memory(memory_path)
        content = (adapter.workspace_path / "memory_setup.py").read_text()
        assert "def add(" in content
        assert "def query(" in content

    def test_healthkit_setup_has_span_and_log(self, tmp_path):
        adapter = self._adapter(tmp_path)
        hk_path = tmp_path / "healthkit"
        hk_path.mkdir()
        adapter.inject_healthkit(hk_path)
        content = (adapter.workspace_path / "healthkit_setup.py").read_text()
        assert "def span(" in content
        assert "def log(" in content


# ---------------------------------------------------------------------------
# __init__ exports
# ---------------------------------------------------------------------------

def test_adapter_exports():
    from agentforge.adapters import (
        BaseAdapter,
        OpenClawAdapter,
        LangChainAdapter,
        AutoGenAdapter,
        StandaloneAdapter,
    )
    assert issubclass(LangChainAdapter, BaseAdapter)
    assert issubclass(StandaloneAdapter, BaseAdapter)
