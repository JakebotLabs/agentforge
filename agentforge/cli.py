"""AgentForge CLI entry point."""

import sys
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from .config import load_config, save_config, AgentForgeConfig, DEFAULT_CONFIG_PATH
from .installer import install_components, check_components, install_all_components
from .runner import start_services, stop_services, get_status

# Force UTF-8 output on Windows to avoid cp1252 encoding errors with Rich
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

console = Console()

PLATFORMS = {
    "1": ("openclaw", "OpenClaw — Full-featured agent runtime"),
    "2": ("langchain", "LangChain — Popular Python agent framework"),
    "3": ("autogen", "AutoGen — Microsoft's multi-agent framework"),
    "4": ("standalone", "Standalone — Raw Python, no framework"),
}


@click.group()
@click.version_option(package_name="agentforge")
def cli():
    """AgentForge — Complete AI agent infrastructure in one command."""
    pass


@cli.command()
@click.option("--platform", type=click.Choice(["openclaw", "langchain", "autogen", "standalone"]), default=None)
@click.option("--workspace", type=click.Path(), default=None)
@click.option("--install/--no-install", default=True, help="Install all components")
def init(platform: str, workspace: str, install: bool):
    """Initialize AgentForge in the current environment."""
    console.print("[bold blue]⚒️  Initializing AgentForge...[/]")
    
    # Interactive platform selection if not provided
    if platform is None:
        console.print("\n[bold]Select your agent platform:[/]\n")
        for key, (name, desc) in PLATFORMS.items():
            console.print(f"  [cyan]{key}[/]) {desc}")
        console.print()
        
        choice = Prompt.ask("Enter choice", choices=["1", "2", "3", "4"], default="4")
        platform = PLATFORMS[choice][0]
        console.print(f"\n  Selected: [green]{platform}[/]\n")
    
    config = AgentForgeConfig(platform=platform)

    # Platform-aware workspace and component path resolution
    if platform == "openclaw":
        # OpenClaw: components already live in the OpenClaw workspace — detect them
        from .adapters.openclaw import OpenClawAdapter
        adapter = OpenClawAdapter()
        if adapter.detect():
            oc_workspace = adapter.get_workspace()
            if oc_workspace:
                config.workspace = oc_workspace
                config.memory.path = oc_workspace / "vector_memory"
                config.healthkit.path = oc_workspace / "healthkit_internal"
                console.print(f"  [green]✓ OpenClaw workspace detected:[/] {oc_workspace}")
            else:
                config.workspace = Path(workspace) if workspace else Path.home() / ".agentforge"
        else:
            console.print("  [yellow]⚠ OpenClaw not detected — using standalone paths[/]")
            config.workspace = Path(workspace) if workspace else Path.home() / ".agentforge"
            config.memory.path = config.workspace / "components" / "agent-memory-core"
            config.healthkit.path = config.workspace / "components" / "agent-healthkit"
    else:
        workspace_path = Path(workspace) if workspace else Path.home() / ".agentforge"
        config.workspace = workspace_path
        config.memory.path = workspace_path / "components" / "agent-memory-core"
        config.healthkit.path = workspace_path / "components" / "agent-healthkit"

    def _component_icon(installed):
        if installed is True:   return "✅"
        if installed is None:   return "🔒"   # Pro / optional
        return "❌"

    # Install or check components
    if install and platform != "openclaw":
        # OpenClaw: components are already installed — no cloning needed
        results = install_all_components(config, console)
        for component, status in results.items():
            icon = _component_icon(status["installed"])
            console.print(f"  {icon} {component}: {status['message']}")
    else:
        results = install_components(config)
        for component, status in results.items():
            icon = _component_icon(status["installed"])
            console.print(f"  {icon} {component}: {status['message']}")
    
    save_config(config)
    console.print(f"\n[green]✓ Config saved to {DEFAULT_CONFIG_PATH}[/]")
    console.print("[green]✓ AgentForge initialized![/]")

    # ── Bootstrap workspace awareness files ───────────────────────────────
    from .bootstrap import bootstrap_workspace

    has_mailbox = (
        (Path.home() / ".openclaw" / "mailbox").exists()
        or (Path.home() / ".agentforge" / "mailbox").exists()
    )
    mailbox_path = Path.home() / ".openclaw" / "mailbox" if has_mailbox else None

    _agentforge_home = Path.home() / ".agentforge"

    console.print("\n[bold blue]📝 Seeding workspace awareness...[/]")
    created = bootstrap_workspace(
        platform=platform,
        workspace_path=config.workspace,
        has_memory=True,
        has_healthkit=True,
        has_mailbox=has_mailbox,
        has_dashboard=True,
        mailbox_path=mailbox_path,
        agentforge_home=_agentforge_home,
    )

    if created:
        for f in created:
            console.print(f"  [green]✓[/] Generated {f}")
        console.print("\n  [dim]Edit SOUL.md to define your mission.[/]")
    else:
        console.print(
            "  [dim]Workspace files already exist — skipping "
            "(won't overwrite your customizations)[/]"
        )

    console.print("\nRun [bold]agentforge start[/] to launch all services.")


@cli.command()
def install():
    """Install or update all AgentForge components."""
    config = load_config()
    console.print("[bold blue]📦 Installing AgentForge components...[/]")
    results = install_all_components(config, console)
    for name, status in results.items():
        icon = "✅" if status["installed"] else "❌"
        console.print(f"  {icon} {name}: {status['message']}")


@cli.command()
@click.option("--dashboard/--no-dashboard", default=True)
@click.option("--healthkit/--no-healthkit", default=True)
def start(dashboard: bool, healthkit: bool):
    """Start AgentForge services."""
    config = load_config()
    console.print("[bold blue]🚀 Starting AgentForge...[/]")
    
    results = start_services(config, dashboard=dashboard, healthkit=healthkit)
    
    for service, status in results.items():
        icon = "✅" if status["running"] else "❌"
        console.print(f"  {icon} {service}: {status['message']}")
    
    if results.get("dashboard", {}).get("running"):
        url = f"http://{config.dashboard.host}:{config.dashboard.port}"
        console.print(f"\n[green]Dashboard running at {url}[/]")


@cli.command()
def stop():
    """Stop all AgentForge services."""
    config = load_config()
    console.print("[yellow]Stopping AgentForge services...[/]")
    stop_services(config)
    console.print("[green]✓ All services stopped[/]")


@cli.command()
def status():
    """Show status of all AgentForge components."""
    config = load_config()
    status_data = get_status(config)
    
    table = Table(title="AgentForge Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    for component, info in status_data.items():
        status_icon = "🟢" if info["healthy"] else "🔴"
        table.add_row(component, f"{status_icon} {info['status']}", info.get("details", ""))
    
    console.print(table)


@cli.command()
def doctor():
    """Check AgentForge installation and diagnose issues."""
    config = load_config()
    console.print("[bold blue]🩺 Running AgentForge diagnostics...[/]")
    
    checks = check_components(config)
    
    all_ok = True
    for check, result in checks.items():
        icon = "✅" if result["ok"] else "❌"
        console.print(f"  {icon} {check}: {result['message']}")
        if not result["ok"]:
            all_ok = False
            if result.get("fix"):
                console.print(f"     💡 Fix: {result['fix']}")
    
    if all_ok:
        console.print("\n[green]All checks passed![/]")
    else:
        console.print("\n[yellow]Some issues found. Run suggested fixes above.[/]")


@cli.command()
@click.argument("bot", type=click.Choice(["codebot", "opusbot"]))
@click.argument("task")
def pipeline(bot: str, task: str):
    """Run a task through the Dev Pipeline (Pro feature).

    \b
    Examples:
      agentforge pipeline codebot "Write a REST API for user auth"
      agentforge pipeline opusbot "Review src/auth.py for security issues"
    """
    import os
    import subprocess as sp

    config = load_config()

    from .components.pipeline import check_pipeline, get_pipeline_root
    check = check_pipeline(config.workspace)

    if not check["installed"]:
        console.print("[yellow]Pipeline not installed.[/]")
        console.print("  Install with: [bold]agentforge install[/]")
        console.print("  Or sponsor at: [cyan]github.com/sponsors/JakebotLabs[/]")
        return

    # Use the pipeline's own venv Python (which has anthropic installed).
    # Falls back to the current interpreter if no venv exists yet.
    from .platform import get_venv_python
    pipeline_root = get_pipeline_root(config.workspace)
    pipeline_python = get_venv_python(pipeline_root)
    if not pipeline_python.exists():
        pipeline_python = Path(sys.executable)

    cmd = [str(pipeline_python), "-m", "pipeline", bot, task]

    env = os.environ.copy()
    env["PYTHONPATH"] = str(pipeline_root) + os.pathsep + env.get("PYTHONPATH", "")

    result = sp.run(cmd, env=env)
    sys.exit(result.returncode)


@cli.group()
def memory():
    """Manage AgentForge persistent memory."""
    pass


@memory.command(name="status")
def memory_status():
    """Check memory system sync status."""
    config = load_config()
    console.print("[bold blue]🧠 Checking memory status...[/]")

    # Locate the vector_memory package inside the workspace
    venv_python = config.memory.path.parent / "vector_memory" / "venv" / "bin" / "python"
    script = config.memory.path.parent / "vector_memory" / "auto_retrieve.py"

    # Fallback: try config.memory.path directly (it might already be vector_memory/)
    if not script.exists():
        venv_python = config.memory.path / "venv" / "bin" / "python"
        script = config.memory.path / "auto_retrieve.py"

    if not script.exists():
        console.print("  [yellow]⚠ Memory script not found.[/]")
        console.print(f"  Expected: {script}")
        console.print("  Run [bold]agentforge install[/] to set up persistent memory.")
        return

    python_cmd = str(venv_python) if venv_python.exists() else sys.executable

    import subprocess as sp
    result = sp.run(
        [python_cmd, str(script), "--status"],
        capture_output=True, text=True,
        cwd=str(script.parent),
    )
    output = (result.stdout + result.stderr).strip()

    if output:
        console.print(output)
    else:
        console.print("  [yellow]No output from memory status check.[/]")

    if result.returncode != 0:
        console.print(
            "\n  [yellow]Memory may be out of sync. "
            "Run [bold]agentforge memory sync[/] to re-index.[/]"
        )
    else:
        console.print("\n  [green]✓ Memory is in sync.[/]")


@memory.command(name="sync")
def memory_sync():
    """Re-index memory system (ChromaDB + NetworkX)."""
    config = load_config()
    console.print("[bold blue]🔄 Syncing memory...[/]")

    # Locate the indexer
    venv_python = config.memory.path.parent / "vector_memory" / "venv" / "bin" / "python"
    script = config.memory.path.parent / "vector_memory" / "indexer.py"

    if not script.exists():
        venv_python = config.memory.path / "venv" / "bin" / "python"
        script = config.memory.path / "indexer.py"

    if not script.exists():
        console.print("  [yellow]⚠ Indexer not found.[/]")
        console.print(f"  Expected: {script}")
        console.print("  Run [bold]agentforge install[/] to set up persistent memory.")
        return

    python_cmd = str(venv_python) if venv_python.exists() else sys.executable

    import subprocess as sp
    console.print("  Running indexer (this may take a moment)...")
    result = sp.run(
        [python_cmd, str(script)],
        cwd=str(script.parent),
    )
    if result.returncode == 0:
        console.print("  [green]✓ Memory sync complete.[/]")
    else:
        console.print("  [red]✗ Indexer exited with errors. Check output above.[/]")


if __name__ == "__main__":
    cli()
