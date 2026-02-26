"""Tests for AgentForge CLI."""

import pytest
from click.testing import CliRunner
from agentforge.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_version(runner):
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_init_help(runner):
    result = runner.invoke(cli, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize AgentForge" in result.output


def test_status_runs(runner):
    result = runner.invoke(cli, ["status"])
    # May show "not initialized" but shouldn't crash
    assert result.exit_code == 0


def test_doctor_runs(runner):
    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
    assert "Python version" in result.output


def test_start_help(runner):
    result = runner.invoke(cli, ["start", "--help"])
    assert result.exit_code == 0
    assert "--dashboard" in result.output


def test_stop_help(runner):
    result = runner.invoke(cli, ["stop", "--help"])
    assert result.exit_code == 0
