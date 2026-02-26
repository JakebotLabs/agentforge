"""AgentForge CLI entry point."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .config import load_config, save_config, AgentForgeConfig, DEFAULT_CONFIG_PATH
from .installer import install_components, check_components
from .runner import start_services, stop_services, get_status

console = Console()


@click.group()
@click.version_option(package_name="agentforge")
def cli():
    """AgentForge — Complete AI agent infrastructure in one command."""
    pass


@cli.command()
@click.option("--platform", type=click.Choice(["openclaw", "langchain", "standalone"]), default="openclaw")
@click.option("--workspace", type=click.Path(), default=None)
def init(platform: str, workspace: str):
    """Initialize AgentForge in the current environment."""
    console.print("[bold blue]⚒️  Initializing AgentForge...[/]")
    
    config = AgentForgeConfig(platform=platform)
    if workspace:
        config.workspace = Path(workspace)
    
    # Check/install components
    results = install_components(config)
    
    for component, status in results.items():
        icon = "✅" if status["installed"] else "❌"
        console.print(f"  {icon} {component}: {status['message']}")
    
    save_config(config)
    console.print(f"\n[green]✓ Config saved to {DEFAULT_CONFIG_PATH}[/]")
    console.print("[green]✓ AgentForge initialized![/]")
    console.print("\nRun [bold]agentforge start[/] to launch all services.")


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


if __name__ == "__main__":
    cli()
