"""Tests for the cross-platform utility module."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from agentforge.platform import (
    get_venv_python,
    get_venv_pip,
    kill_process,
    check_process_exists,
    popen_detached,
)


class TestGetVenvPython:
    def test_windows_path(self):
        with patch("agentforge.platform.IS_WINDOWS", True):
            result = get_venv_python(Path("/some/project"))
            assert result == Path("/some/project/venv/Scripts/python.exe")

    def test_unix_path(self):
        with patch("agentforge.platform.IS_WINDOWS", False):
            result = get_venv_python(Path("/some/project"))
            assert result == Path("/some/project/venv/bin/python")

    def test_returns_path_object(self):
        result = get_venv_python(Path("/test"))
        assert isinstance(result, Path)


class TestGetVenvPip:
    def test_windows_path(self):
        with patch("agentforge.platform.IS_WINDOWS", True):
            result = get_venv_pip(Path("/some/project"))
            assert result == Path("/some/project/venv/Scripts/pip.exe")

    def test_unix_path(self):
        with patch("agentforge.platform.IS_WINDOWS", False):
            result = get_venv_pip(Path("/some/project"))
            assert result == Path("/some/project/venv/bin/pip")


class TestKillProcess:
    def test_windows_uses_taskkill(self):
        with patch("agentforge.platform.IS_WINDOWS", True), \
             patch("subprocess.run") as mock_run:
            kill_process(1234)
            mock_run.assert_called_once_with(
                ["taskkill", "/F", "/PID", "1234"],
                capture_output=True,
            )

    def test_unix_uses_sigterm(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("os.kill") as mock_kill:
            import signal
            kill_process(1234)
            mock_kill.assert_called_once_with(1234, signal.SIGTERM)

    def test_returns_true_on_success(self):
        with patch("agentforge.platform.IS_WINDOWS", True), \
             patch("subprocess.run"):
            assert kill_process(1234) is True

    def test_returns_false_on_process_not_found(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("os.kill", side_effect=ProcessLookupError):
            assert kill_process(99999) is False


class TestCheckProcessExists:
    def test_windows_queries_tasklist(self):
        mock_result = MagicMock()
        mock_result.stdout = "python.exe                    1234 Console"
        with patch("agentforge.platform.IS_WINDOWS", True), \
             patch("subprocess.run", return_value=mock_result):
            assert check_process_exists(1234) is True

    def test_windows_returns_false_when_not_found(self):
        mock_result = MagicMock()
        mock_result.stdout = "INFO: No tasks are running"
        with patch("agentforge.platform.IS_WINDOWS", True), \
             patch("subprocess.run", return_value=mock_result):
            assert check_process_exists(99999) is False

    def test_unix_uses_signal_zero(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("os.kill") as mock_kill:
            assert check_process_exists(1234) is True
            mock_kill.assert_called_once_with(1234, 0)

    def test_unix_returns_false_on_not_found(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("os.kill", side_effect=ProcessLookupError):
            assert check_process_exists(99999) is False


class TestPopenDetached:
    def test_windows_uses_creation_flags(self):
        with patch("agentforge.platform.IS_WINDOWS", True), \
             patch("subprocess.Popen") as mock_popen:
            popen_detached(["echo", "hello"])
            call_kwargs = mock_popen.call_args[1]
            assert "creationflags" in call_kwargs
            expected = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
            assert call_kwargs["creationflags"] == expected
            assert "start_new_session" not in call_kwargs

    def test_unix_uses_start_new_session(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("subprocess.Popen") as mock_popen:
            popen_detached(["echo", "hello"])
            call_kwargs = mock_popen.call_args[1]
            assert call_kwargs.get("start_new_session") is True
            assert "creationflags" not in call_kwargs

    def test_passes_extra_kwargs(self):
        with patch("agentforge.platform.IS_WINDOWS", False), \
             patch("subprocess.Popen") as mock_popen:
            popen_detached(["echo"], cwd="/tmp", stdout=subprocess.DEVNULL)
            call_kwargs = mock_popen.call_args[1]
            assert call_kwargs["cwd"] == "/tmp"
            assert call_kwargs["stdout"] == subprocess.DEVNULL
