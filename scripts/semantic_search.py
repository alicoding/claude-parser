#!/usr/bin/env python3
"""
Semantic search CLI for Claude Parser codebase.

95/5: Using typer for CLI, llama-index for search
SOLID: Single entry point for semantic queries
"""

import typer
from rich.console import Console
from rich.table import Table
from rich import box
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = typer.Typer(help="Semantic search for Claude Parser codebase")
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    top_k: int = typer.Option(5, help="Number of results"),
    show_content: bool = typer.Option(False, help="Show content preview"),
):
    """Search codebase using semantic search."""
    try:
        from claude_parser.semantic import SemanticSearch

        searcher = SemanticSearch()
        results = searcher.search(query, top_k=top_k)

        if not results:
            console.print("[yellow]No results found[/yellow]")
            return

        # Display results
        table = Table(
            title=f"Search Results for: {query}",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )

        table.add_column("File", style="cyan")
        table.add_column("Score", style="green")
        if show_content:
            table.add_column("Preview", style="dim")

        for result in results:
            row = [
                result["file"],
                f"{result.get('score', 0):.3f}"
            ]
            if show_content:
                preview = result["content"][:100] + "..."
                row.append(preview)

            table.add_row(*row)

        console.print(table)

    except ImportError as e:
        console.print(f"[red]Error: Missing dependencies. Install: pip install llama-index[/red]")
        console.print(f"[dim]{e}[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def find_similar(
    file_path: Path = typer.Argument(..., help="File to find similar code"),
    top_k: int = typer.Option(5, help="Number of results"),
):
    """Find code similar to a given file."""
    try:
        from claude_parser.semantic import SemanticSearch

        if not file_path.exists():
            console.print(f"[red]File not found: {file_path}[/red]")
            return

        # Use file content as query
        content = file_path.read_text()[:500]  # First 500 chars

        searcher = SemanticSearch()
        results = searcher.search(content, top_k=top_k + 1)  # +1 to skip self

        # Filter out the same file
        results = [r for r in results if r["file"] != str(file_path)][:top_k]

        console.print(f"[bold]Files similar to {file_path.name}:[/bold]")
        for i, result in enumerate(results, 1):
            console.print(f"{i}. [cyan]{result['file']}[/cyan] (score: {result.get('score', 0):.3f})")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


@app.command()
def complexity(
    query: str = typer.Argument(..., help="Find complex code related to query"),
):
    """Find complex code areas related to query."""
    try:
        from claude_parser.semantic import SemanticSearch

        searcher = SemanticSearch()

        # Search for complexity-related terms
        complex_query = f"{query} complexity cyclomatic high difficult complex"
        results = searcher.search(complex_query, top_k=10)

        console.print(f"[bold]Complex areas related to: {query}[/bold]")
        for result in results:
            if any(word in result["content"].lower() for word in ["complex", "difficult", "todo", "fixme"]):
                console.print(f"• [yellow]{result['file']}[/yellow]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    app()
