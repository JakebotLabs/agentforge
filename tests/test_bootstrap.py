"""Tests for agentforge.bootstrap — workspace file generation."""

import sys
from pathlib import Path
from datetime import datetime

import pytest

# Allow import without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))
from agentforge.bootstrap import bootstrap_workspace


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def workspace(tmp_path):
    """A clean temporary workspace directory."""
    return tmp_path / "workspace"


@pytest.fixture
def agentforge_home(tmp_path):
    """A clean temporary agentforge home."""
    return tmp_path / ".agentforge"


# ──────────────────────────────────────────────────────────────────────────────
# Test 1: All expected files are created
# ──────────────────────────────────────────────────────────────────────────────

class TestBootstrapCreatesFiles:

    def test_creates_agents_md(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "AGENTS.md" in created
        assert (workspace / "AGENTS.md").exists()

    def test_creates_heartbeat_md(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "HEARTBEAT.md" in created
        assert (workspace / "HEARTBEAT.md").exists()

    def test_creates_memory_md(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "MEMORY.md" in created
        assert (workspace / "MEMORY.md").exists()

    def test_creates_soul_md(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "SOUL.md" in created
        assert (workspace / "SOUL.md").exists()

    def test_creates_identity_md(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "IDENTITY.md" in created
        assert (workspace / "IDENTITY.md").exists()

    def test_creates_memory_directory_and_log(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=True,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "memory").is_dir()
        # At least one file in memory/ directory should be in created list
        memory_files = [c for c in created if c.startswith("memory/")]
        assert len(memory_files) == 1

    def test_workspace_dir_created_if_missing(self, tmp_path, agentforge_home):
        workspace = tmp_path / "does" / "not" / "exist"
        assert not workspace.exists()
        bootstrap_workspace(
            platform="standalone",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert workspace.exists()

    def test_returns_list_of_created_filenames(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert isinstance(created, list)
        assert len(created) >= 5  # AGENTS, HEARTBEAT, MEMORY, SOUL, IDENTITY


# ──────────────────────────────────────────────────────────────────────────────
# Test 2: Files are NOT overwritten (user customization protection)
# ──────────────────────────────────────────────────────────────────────────────

class TestNoOverwrite:

    def test_existing_agents_md_not_overwritten(self, workspace, agentforge_home):
        workspace.mkdir(parents=True)
        original = "# My custom AGENTS.md\nDo not touch."
        (workspace / "AGENTS.md").write_text(original)

        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "AGENTS.md").read_text() == original

    def test_existing_soul_md_not_overwritten(self, workspace, agentforge_home):
        workspace.mkdir(parents=True)
        original = "# My custom SOUL.md\nTop secret mission."
        (workspace / "SOUL.md").write_text(original)

        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "SOUL.md").read_text() == original

    def test_existing_heartbeat_md_not_overwritten(self, workspace, agentforge_home):
        workspace.mkdir(parents=True)
        original = "# My heartbeat\nCustom steps."
        (workspace / "HEARTBEAT.md").write_text(original)

        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "HEARTBEAT.md").read_text() == original

    def test_existing_files_not_in_created_list(self, workspace, agentforge_home):
        workspace.mkdir(parents=True)
        (workspace / "SOUL.md").write_text("existing")
        (workspace / "AGENTS.md").write_text("existing")

        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        assert "SOUL.md" not in created
        assert "AGENTS.md" not in created

    def test_second_run_creates_nothing(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        # Second run — all files exist
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        # Only memory log might be skipped; other files already exist
        non_memory = [c for c in created if not c.startswith("memory/")]
        assert non_memory == []


# ──────────────────────────────────────────────────────────────────────────────
# Test 3: AGENTS.md contains correct platform-specific sections
# ──────────────────────────────────────────────────────────────────────────────

class TestAgentsMdContent:

    def _get_agents_md(self, workspace, agentforge_home, **kwargs):
        bootstrap_workspace(
            workspace_path=workspace,
            agentforge_home=agentforge_home,
            **kwargs,
        )
        return (workspace / "AGENTS.md").read_text()

    def test_contains_installed_stack_header(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw"
        )
        assert "Your Installed Stack" in content

    def test_openclaw_section_present_for_openclaw_platform(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw"
        )
        assert "OpenClaw Config" in content
        assert "openclaw config set" in content
        assert "openclaw.json" in content

    def test_openclaw_section_absent_for_standalone_platform(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="standalone"
        )
        assert "OpenClaw Config" not in content

    def test_memory_protocol_present_when_has_memory(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_memory=True
        )
        assert "Memory Protocol" in content
        assert "memory_search" in content

    def test_memory_protocol_absent_when_no_memory(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_memory=False
        )
        assert "memory_search" not in content

    def test_autonomy_tiers_always_present(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="standalone",
            has_memory=False, has_healthkit=False
        )
        assert "Autonomy Tiers" in content
        assert "Tier 1" in content
        assert "Tier 3" in content

    def test_healthkit_section_present_when_installed(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_healthkit=True
        )
        assert "HealthKit Protocol" in content

    def test_dashboard_section_present_when_installed(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_dashboard=True
        )
        assert "Dashboard" in content

    def test_mailbox_section_present_when_has_mailbox(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_mailbox=True
        )
        assert "Mailbox Protocol" in content
        assert "Listen Before You Speak" in content

    def test_mailbox_section_absent_when_no_mailbox(self, workspace, agentforge_home):
        content = self._get_agents_md(
            workspace, agentforge_home, platform="openclaw", has_mailbox=False
        )
        assert "Mailbox Protocol" not in content


# ──────────────────────────────────────────────────────────────────────────────
# Test 4: HEARTBEAT.md contains mailbox step only when has_mailbox=True
# ──────────────────────────────────────────────────────────────────────────────

class TestHeartbeatMdContent:

    def _get_heartbeat(self, workspace, agentforge_home, **kwargs):
        bootstrap_workspace(
            workspace_path=workspace,
            agentforge_home=agentforge_home,
            **kwargs,
        )
        return (workspace / "HEARTBEAT.md").read_text()

    def test_mailbox_step_present_when_has_mailbox(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_mailbox=True,
        )
        assert "Mailbox Check" in content
        assert "mailbox_check.py" in content

    def test_mailbox_step_absent_when_no_mailbox(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_mailbox=False,
        )
        assert "Mailbox Check" not in content

    def test_health_check_step_present(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_healthkit=True,
        )
        assert "Health Check" in content
        assert "agentforge status" in content

    def test_memory_sync_step_present_when_has_memory(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_memory=True,
        )
        assert "Memory Sync" in content
        assert "agentforge memory status" in content

    def test_memory_sync_step_absent_when_no_memory(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_memory=False,
        )
        assert "agentforge memory status" not in content

    def test_project_pipeline_always_present(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="standalone",
            has_memory=False, has_healthkit=False, has_mailbox=False,
        )
        assert "Project Pipeline" in content
        assert "PROJECTS.md" in content

    def test_mailbox_is_step_0(self, workspace, agentforge_home):
        """When mailbox is present, it must be the first step (Step 0)."""
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw", has_mailbox=True,
        )
        mailbox_pos = content.find("Mailbox Check")
        health_pos = content.find("Health Check")
        assert mailbox_pos < health_pos, "Mailbox step must come before Health Check"

    def test_heartbeat_ok_present(self, workspace, agentforge_home):
        content = self._get_heartbeat(
            workspace, agentforge_home,
            platform="openclaw",
        )
        assert "HEARTBEAT_OK" in content


# ──────────────────────────────────────────────────────────────────────────────
# Test 5: mailbox_check.py generated only when has_mailbox=True + path provided
# ──────────────────────────────────────────────────────────────────────────────

class TestMailboxCheckPy:

    def test_generated_when_has_mailbox_and_path(self, workspace, agentforge_home, tmp_path):
        mailbox_path = tmp_path / "mailbox"
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=True,
            mailbox_path=mailbox_path,
            agentforge_home=agentforge_home,
        )
        assert "mailbox_check.py" in created
        assert (workspace / "mailbox_check.py").exists()

    def test_not_generated_when_has_mailbox_false(self, workspace, agentforge_home, tmp_path):
        mailbox_path = tmp_path / "mailbox"
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=False,
            mailbox_path=mailbox_path,
            agentforge_home=agentforge_home,
        )
        assert "mailbox_check.py" not in created
        assert not (workspace / "mailbox_check.py").exists()

    def test_not_generated_when_mailbox_path_none(self, workspace, agentforge_home):
        created = bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=True,
            mailbox_path=None,
            agentforge_home=agentforge_home,
        )
        assert "mailbox_check.py" not in created
        assert not (workspace / "mailbox_check.py").exists()

    def test_mailbox_check_contains_correct_path(self, workspace, agentforge_home, tmp_path):
        mailbox_path = tmp_path / "my_mailbox"
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=True,
            mailbox_path=mailbox_path,
            agentforge_home=agentforge_home,
        )
        content = (workspace / "mailbox_check.py").read_text()
        assert str(mailbox_path) in content
        assert "mailbox.py" in content
        assert "check_inbox" in content

    def test_mailbox_check_is_executable_python(self, workspace, agentforge_home, tmp_path):
        mailbox_path = tmp_path / "mailbox"
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=True,
            mailbox_path=mailbox_path,
            agentforge_home=agentforge_home,
        )
        content = (workspace / "mailbox_check.py").read_text()
        assert content.startswith("#!/usr/bin/env python3")
        assert "def main():" in content
        assert '__name__ == "__main__"' in content

    def test_mailbox_check_not_overwritten_if_exists(self, workspace, agentforge_home, tmp_path):
        workspace.mkdir(parents=True)
        original = "# custom mailbox checker"
        (workspace / "mailbox_check.py").write_text(original)
        mailbox_path = tmp_path / "mailbox"

        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_mailbox=True,
            mailbox_path=mailbox_path,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "mailbox_check.py").read_text() == original


# ──────────────────────────────────────────────────────────────────────────────
# Test 6: memory/ directory and starter log are created
# ──────────────────────────────────────────────────────────────────────────────

class TestMemorySeeding:

    def test_memory_dir_created(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=True,
            agentforge_home=agentforge_home,
        )
        assert (workspace / "memory").is_dir()

    def test_starter_log_created_with_today_date(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=True,
            agentforge_home=agentforge_home,
        )
        today = datetime.now().strftime("%Y-%m-%d")
        assert (workspace / "memory" / f"{today}.md").exists()

    def test_starter_log_content(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=True,
            agentforge_home=agentforge_home,
        )
        today = datetime.now().strftime("%Y-%m-%d")
        content = (workspace / "memory" / f"{today}.md").read_text()
        assert "AgentForge" in content
        assert "bootstrap: complete" in content
        assert "memory_search" in content

    def test_memory_not_seeded_when_has_memory_false(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=False,
            agentforge_home=agentforge_home,
        )
        # memory/ dir should not be created
        assert not (workspace / "memory").exists()

    def test_existing_log_not_overwritten(self, workspace, agentforge_home):
        workspace.mkdir(parents=True)
        memory_dir = workspace / "memory"
        memory_dir.mkdir()
        today = datetime.now().strftime("%Y-%m-%d")
        existing_log = memory_dir / f"{today}.md"
        original = "# My existing log — do not overwrite"
        existing_log.write_text(original)

        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            has_memory=True,
            agentforge_home=agentforge_home,
        )
        assert existing_log.read_text() == original


# ──────────────────────────────────────────────────────────────────────────────
# Additional: MEMORY.md and IDENTITY.md content checks
# ──────────────────────────────────────────────────────────────────────────────

class TestMemoryMdContent:

    def _get_memory_md(self, workspace, agentforge_home, **kwargs):
        bootstrap_workspace(
            workspace_path=workspace,
            agentforge_home=agentforge_home,
            **kwargs,
        )
        return (workspace / "MEMORY.md").read_text()

    def test_contains_stack_table(self, workspace, agentforge_home):
        content = self._get_memory_md(workspace, agentforge_home, platform="openclaw")
        assert "Component" in content
        assert "Status" in content

    def test_agentforge_version_present(self, workspace, agentforge_home):
        content = self._get_memory_md(workspace, agentforge_home, platform="openclaw")
        assert "agentforge_version: 0.1.0" in content

    def test_platform_in_content(self, workspace, agentforge_home):
        content = self._get_memory_md(workspace, agentforge_home, platform="langchain")
        assert "langchain" in content

    def test_mailbox_active_row_when_installed(self, workspace, agentforge_home, tmp_path):
        mailbox_path = tmp_path / "mailbox"
        content = self._get_memory_md(
            workspace, agentforge_home,
            platform="openclaw",
            has_mailbox=True,
            mailbox_path=mailbox_path,
        )
        assert "✅ Active" in content
        assert str(mailbox_path) in content

    def test_mailbox_not_installed_row_when_absent(self, workspace, agentforge_home):
        content = self._get_memory_md(
            workspace, agentforge_home,
            platform="openclaw",
            has_mailbox=False,
        )
        assert "Not installed" in content


class TestIdentityMdContent:

    def test_platform_in_identity(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="autogen",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        content = (workspace / "IDENTITY.md").read_text()
        assert "autogen" in content

    def test_docs_link_present(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        content = (workspace / "IDENTITY.md").read_text()
        assert "agentsforge.dev" in content

    def test_version_in_identity(self, workspace, agentforge_home):
        bootstrap_workspace(
            platform="openclaw",
            workspace_path=workspace,
            agentforge_home=agentforge_home,
        )
        content = (workspace / "IDENTITY.md").read_text()
        assert "0.1.0" in content
