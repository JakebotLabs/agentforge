"""Dev pipeline component — CodeBot, OpusBot, and orchestrator."""
from pathlib import Path
import subprocess
import sys

PIPELINE_REPO = "https://github.com/JakebotLabs/agentforge.git"
PIPELINE_SUBDIR = "pipeline"  # We'll create this in the main repo

def check_pipeline(workspace: Path) -> dict:
    """Check if dev pipeline is installed."""
    pipeline_path = workspace / "pipeline"
    orchestrator = pipeline_path / "orchestrate.py"
    
    if orchestrator.exists():
        return {"installed": True, "path": str(pipeline_path)}
    return {"installed": False, "path": None}

def get_pipeline_status(workspace: Path) -> dict:
    """Get pipeline status."""
    check = check_pipeline(workspace)
    if check["installed"]:
        return {"healthy": True, "status": "Ready", "details": "CodeBot + OpusBot available"}
    return {
        "healthy": None,   # None = not an error, just not available
        "status": "Pro feature",
        "details": "github.com/sponsors/JakebotLabs",
    }
