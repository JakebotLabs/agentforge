"""Cross-platform utilities for AgentForge.

Centralizes all platform-specific logic (Windows vs Unix) so the rest of
the codebase can stay platform-agnostic.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, Optional

IS_WINDOWS = sys.platform == "win32"


def get_venv_python(base_path: Path) -> Path:
    """Return the path to the Python executable inside a venv.

    On Windows: ``base_path / venv / Scripts / python.exe``
    On Unix:    ``base_path / venv / bin / python``
    """
    if IS_WINDOWS:
        return base_path / "venv" / "Scripts" / "python.exe"
    return base_path / "venv" / "bin" / "python"


def get_venv_pip(base_path: Path) -> Path:
    """Return the path to pip inside a venv.

    On Windows: ``base_path / venv / Scripts / pip.exe``
    On Unix:    ``base_path / venv / bin / pip``
    """
    if IS_WINDOWS:
        return base_path / "venv" / "Scripts" / "pip.exe"
    return base_path / "venv" / "bin" / "pip"


def kill_process(pid: int) -> bool:
    """Terminate a process by PID. Returns True if successful."""
    try:
        if IS_WINDOWS:
            # taskkill is the reliable way to kill processes on Windows
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid)],
                capture_output=True,
            )
        else:
            import signal
            os.kill(pid, signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def check_process_exists(pid: int) -> bool:
    """Check whether a process with the given PID is still running."""
    try:
        if IS_WINDOWS:
            # On Windows, query tasklist for the specific PID
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        else:
            # On Unix, signal 0 checks existence without actually signaling
            os.kill(pid, 0)
            return True
    except (ProcessLookupError, PermissionError, OSError):
        return False


def popen_detached(cmd: list, **kwargs: Any) -> subprocess.Popen:
    """Launch a subprocess detached from the parent process.

    On Unix:    uses ``start_new_session=True``
    On Windows: uses ``CREATE_NEW_PROCESS_GROUP`` creation flag
    """
    if IS_WINDOWS:
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True

    return subprocess.Popen(cmd, **kwargs)
