"""
Typer extension - 95/5 framework extension for CLI commands.

95%: Typer does ALL the CLI handling
5%: Simple command definitions
"""

import typer
from typing import Optional
from pathlib import Path
from ..core.resources import ResourceManager


app = typer.Typer(help="Claude Parser CLI - Framework-driven commands")


class CLIExtension:
    """Micro-component: Extend Typer for CLI (10 LOC)."""

    def __init__(self, resources: ResourceManager):
        self.resources = resources


@app.command()
def analyze(
    file_path: Path = typer.Argument(..., help="Path to JSONL file"),
    format: str = typer.Option("json", help="Output format")
):
    """Analyze conversation - Typer handles all CLI complexity."""
    from ..api.factory import analyze_conversation
    result = analyze_conversation(str(file_path))

    if format == "json":
        typer.echo(result)
    else:
        typer.echo(f"Analysis: {result}")


@app.command()
def watch(
    file_path: Path = typer.Argument(..., help="Path to JSONL file"),
    format: str = typer.Option("text", help="Output format")
):
    """Watch file for changes - Typer + watchfiles do everything."""
    from ..api.factory import watch_conversation
    typer.echo(f"Watching {file_path}...")

    for conversation, new_messages in watch_conversation(str(file_path)):
        typer.echo(f"New messages: {len(new_messages)}")


@app.command()
def timeline(
    directory: Path = typer.Argument(..., help="Directory with JSONL files")
):
    """Create timeline - Git + Rich do all the work."""
    from ..api.factory import create_timeline
    timeline = create_timeline(directory)
    typer.echo(f"Timeline created with {len(timeline.events)} events")


if __name__ == "__main__":
    app()  # Typer handles everything
