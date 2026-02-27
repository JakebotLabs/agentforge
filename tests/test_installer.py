"""Tests for the component installer."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agentforge.installer import install_all_components, install_components, check_components
from agentforge.config import AgentForgeConfig


@pytest.fixture
def config(tmp_path):
    """Create a test config with temp paths."""
    return AgentForgeConfig(
        workspace=tmp_path / "workspace",
        memory={"path": tmp_path / "memory"},
        healthkit={"path": tmp_path / "healthkit"},
    )


class TestInstallAllComponents:
    def test_clones_repos_when_not_present(self, config):
        """install_all_components should call git clone for missing repos."""
        console = MagicMock()
        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stderr = ""

        with patch("subprocess.run", return_value=success_result):
            results = install_all_components(config, console)

        # Should attempt to install all 4 components
        assert "agent-memory-core" in results
        assert "agent-healthkit" in results
        assert "jakebot-dashboard" in results
        assert "pipeline" in results

    def test_updates_existing_repos(self, config, tmp_path):
        """If a component directory already exists, should git pull."""
        console = MagicMock()
        # Create the components dir and a fake existing repo
        components_dir = tmp_path / "workspace" / "components"
        components_dir.mkdir(parents=True)
        (components_dir / "agent-memory-core").mkdir()

        success_result = MagicMock()
        success_result.returncode = 0
        success_result.stderr = ""

        with patch("subprocess.run", return_value=success_result):
            results = install_all_components(config, console)

        assert results["agent-memory-core"]["message"] == "Updated"

    def test_pro_feature_graceful_fallback(self, config):
        """Pipeline clone failure due to auth should show Pro message."""
        console = MagicMock()
        call_count = [0]

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            call_count[0] += 1
            if "agentforge-pipeline" in str(cmd):
                result.returncode = 128
                result.stderr = "fatal: Authentication failed for 'https://github.com/...'"
            else:
                result.returncode = 0
                result.stderr = ""
            return result

        with patch("subprocess.run", side_effect=mock_run):
            results = install_all_components(config, console)

        assert results["pipeline"]["locked"] is True
        assert "Pro feature" in results["pipeline"]["message"]


class TestInstallComponents:
    def test_detects_existing_memory(self, config, tmp_path):
        """Should detect existing ChromaDB directory."""
        memory_path = tmp_path / "memory"
        memory_path.mkdir(parents=True)
        (memory_path / "chroma_db").mkdir()

        results = install_components(config)
        assert results["agent-memory-core"]["installed"] is True

    def test_reports_missing_memory(self, config):
        """Should report missing memory system."""
        results = install_components(config)
        assert results["agent-memory-core"]["installed"] is False

    def test_detects_existing_healthkit(self, config, tmp_path):
        """Should detect existing healthkit monitor."""
        healthkit_path = tmp_path / "healthkit"
        healthkit_path.mkdir(parents=True)
        (healthkit_path / "monitor.py").write_text("# monitor")

        results = install_components(config)
        assert results["agent-healthkit"]["installed"] is True


class TestCheckComponents:
    def test_python_version_check(self, config):
        """Should pass Python version check (we're running 3.10+)."""
        checks = check_components(config)
        assert checks["Python version"]["ok"] is True

    def test_pipeline_never_fails(self, config):
        """Pipeline check should always be ok (Pro is optional)."""
        checks = check_components(config)
        assert checks["Pipeline"]["ok"] is True
