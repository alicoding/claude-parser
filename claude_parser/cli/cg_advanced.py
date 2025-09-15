#!/usr/bin/env python3
"""
Advanced Git-like commands for Claude Parser
@SINGLE_SOURCE_TRUTH: Separated from cg.py to maintain <80 LOC per file
@FRAMEWORK_FIRST: 100% delegation to query modules
"""
import typer
from rich.console import Console
from rich.table import Table
from ..discovery import discover_current_project_files
from ..queries import find_queries, blame_queries, reflog_queries
from ..navigation import find_message_by_uuid
from .. import load_latest_session

app = typer.Typer()
console = Console()


@app.command()
def find(pattern: str = typer.Argument(..., help="Pattern to search for")):
    """Find files in any message (like git log --all --grep)"""
    files = discover_current_project_files()
    if not files:
        console.print("No Claude sessions found", style="yellow")
        return

    jsonl_paths = [str(f) for f in files]
    results = find_queries.find_files(pattern, jsonl_paths)

    if not results:
        console.print(f"No files matching '{pattern}' found", style="yellow")
        return

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("UUID", style="cyan", width=12)
    table.add_column("File", style="green")
    table.add_column("Time", style="dim")
    table.add_column("Tool", style="yellow")

    for uuid, file_path, timestamp, tool in results[:20]:
        table.add_row(str(uuid)[:8] + "...", file_path, str(timestamp)[:19], tool)

    console.print(table)
    if len(results) > 20:
        console.print(f"\n... and {len(results)-20} more results", style="dim")


@app.command()
def blame(file: str = typer.Argument(..., help="File to blame")):
    """Show who last modified file (like git blame)"""
    files = discover_current_project_files()
    if not files:
        console.print("No Claude sessions found", style="yellow")
        return

    jsonl_paths = [str(f) for f in files]
    results = blame_queries.blame_file(file, jsonl_paths)

    if not results:
        console.print(f"No modifications found for '{file}'", style="yellow")
        return

    uuid, timestamp, tool, tool_input = results[0]
    console.print(f"\nLast modified by:", style="bold")
    console.print(f"  UUID: {uuid[:8]}...", style="cyan")
    console.print(f"  Time: {timestamp}", style="dim")
    console.print(f"  Tool: {tool}", style="yellow")


