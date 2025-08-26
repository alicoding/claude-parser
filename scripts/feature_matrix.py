#!/usr/bin/env python3
"""
Generate feature matrix documentation for Claude Parser SDK.

95/5: Using typer for CLI, rich for display
SOLID: Single responsibility - only feature matrix generation
"""

import typer
from rich.console import Console
from rich.table import Table
from rich import box
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_parser.features import get_registry, FeatureStatus
from claude_parser.features.registry import save_registry
from claude_parser.features.formatters import to_markdown_table

app = typer.Typer(help="Feature Matrix Generator for Claude Parser SDK")
console = Console()


@app.command()
def show(
    category: str = typer.Option(None, help="Filter by category"),
    status: str = typer.Option(None, help="Filter by status"),
    incomplete: bool = typer.Option(False, help="Show only incomplete features"),
):
    """Display feature matrix in terminal."""
    registry = get_registry()
    
    # Create rich table
    table = Table(
        title=f"Claude Parser SDK v{registry.version} - Feature Matrix",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    
    # Add columns
    table.add_column("Feature", style="cyan")
    table.add_column("Category", style="yellow")
    table.add_column("Status", style="white")
    table.add_column("Tests", style="green")
    table.add_column("Coverage", style="blue")
    table.add_column("Notes", style="dim")
    
    # Filter features
    features = registry.features
    if category:
        features = [f for f in features if f.category.value == category.lower()]
    if status:
        features = [f for f in features if f.status.value == status.lower()]
    if incomplete:
        features = registry.get_incomplete_features()
    
    # Add rows
    for f in features:
        # Status with emoji
        status_display = {
            FeatureStatus.COMPLETE: "[green]✅ complete[/green]",
            FeatureStatus.PARTIAL: "[yellow]🚧 partial[/yellow]",
            FeatureStatus.BETA: "[blue]🔵 beta[/blue]",
            FeatureStatus.EXPERIMENTAL: "[magenta]🧪 experimental[/magenta]",
            FeatureStatus.DEPRECATED: "[red]⚠️ deprecated[/red]",
            FeatureStatus.PLANNED: "[dim]📋 planned[/dim]",
            FeatureStatus.NOT_STARTED: "[dim]⭕ not started[/dim]"
        }.get(f.status, f.status.value)
        
        # Test info
        if f.tests_total:
            tests = f"[green]{f.tests_passing}[/green]/{f.tests_total}"
            if f.tests_passing < f.tests_total:
                tests = f"[yellow]{f.tests_passing}[/yellow]/{f.tests_total}"
        else:
            tests = "[dim]N/A[/dim]"
        
        # Coverage
        if f.coverage_percent is not None:
            if f.coverage_percent >= 90:
                coverage = f"[green]{f.coverage_percent:.1f}%[/green]"
            elif f.coverage_percent >= 70:
                coverage = f"[yellow]{f.coverage_percent:.1f}%[/yellow]"
            else:
                coverage = f"[red]{f.coverage_percent:.1f}%[/red]"
        else:
            coverage = "[dim]N/A[/dim]"
        
        # Notes (truncate if too long)
        notes = f.notes or ""
        if len(notes) > 40:
            notes = notes[:37] + "..."
        
        table.add_row(
            f.name,
            f.category.value,
            status_display,
            tests,
            coverage,
            notes
        )
    
    console.print(table)
    
    # Summary statistics
    console.print("\n[bold]Summary:[/bold]")
    complete = len(registry.get_complete_features())
    incomplete = len(registry.get_incomplete_features())
    deprecated = len(registry.get_deprecated_features())
    total = len(registry.features)
    
    console.print(f"  • Complete: [green]{complete}/{total}[/green]")
    console.print(f"  • Incomplete: [yellow]{incomplete}/{total}[/yellow]")
    console.print(f"  • Deprecated: [red]{deprecated}[/red]")


@app.command()
def markdown(output: Path = typer.Option(Path("docs/api/FEATURES.md"), help="Output file")):
    """Generate markdown documentation."""
    registry = get_registry()
    
    content = [
        f"# Claude Parser SDK - Feature Matrix",
        f"",
        f"**Version**: {registry.version}",
        f"**Updated**: {registry.updated[:10]}",
        f"",
        f"## Feature Status",
        f"",
        to_markdown_table(registry),
        f"",
        f"## Status Definitions",
        f"",
        f"- ✅ **complete**: Fully implemented with 100% test coverage",
        f"- 🚧 **partial**: Partially implemented, some features missing",
        f"- 🔵 **beta**: Complete but may have breaking changes",
        f"- 🧪 **experimental**: Experimental feature, API may change",
        f"- ⚠️ **deprecated**: Deprecated, will be removed in future version",
        f"- 📋 **planned**: Planned for future implementation",
        f"- ⭕ **not_started**: Not yet started",
        f"",
        f"## Capability Matrix by Category",
        f"",
        f"```json",
        f"{registry.to_capability_matrix()}",
        f"```",
        f"",
        f"## Incomplete Features",
        f"",
    ]
    
    incomplete = registry.get_incomplete_features()
    if incomplete:
        for f in incomplete:
            deps = f", ".join(f.depends_on) if f.depends_on else "None"
            content.append(f"### {f.name}")
            content.append(f"- **Status**: {f.status.value}")
            content.append(f"- **Category**: {f.category.value}")
            content.append(f"- **Description**: {f.description}")
            content.append(f"- **Dependencies**: {deps}")
            if f.notes:
                content.append(f"- **Notes**: {f.notes}")
            content.append("")
    else:
        content.append("All features are complete! 🎉")
    
    # Write file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(content))
    
    console.print(f"[green]✅ Generated feature matrix:[/green] {output}")


@app.command()
def save():
    """Save registry to JSON file."""
    save_registry()
    console.print("[green]✅ Saved feature registry to docs/api/FEATURES.json[/green]")


@app.command()
def check():
    """Check for incomplete features and unused imports."""
    registry = get_registry()
    incomplete = registry.get_incomplete_features()
    
    if incomplete:
        console.print("[yellow]⚠️ Incomplete features found:[/yellow]")
        for f in incomplete:
            console.print(f"  • {f.name} ({f.category.value}): {f.status.value}")
            if f.notes:
                console.print(f"    [dim]{f.notes}[/dim]")
        
        # Check for unused imports indicator
        partial_with_notes = [f for f in incomplete if f.status == FeatureStatus.PARTIAL and f.notes]
        if partial_with_notes:
            console.print("\n[red]🔍 Features with unused imports (incomplete implementation):[/red]")
            for f in partial_with_notes:
                if "unused" in f.notes.lower():
                    console.print(f"  • {f.name}: {f.notes}")
        
        return 1  # Exit with error code
    else:
        console.print("[green]✅ All features complete![/green]")
        return 0


if __name__ == "__main__":
    app()
