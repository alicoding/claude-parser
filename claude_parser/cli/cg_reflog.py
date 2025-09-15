#!/usr/bin/env python3
"""
Reflog and show commands for Claude Parser
@SINGLE_SOURCE_TRUTH: Separated from cg.py to maintain <80 LOC per file
@FRAMEWORK_FIRST: 100% delegation to query modules
"""
import typer
from rich.console import Console
from ..discovery import discover_current_project_files
from ..queries import reflog_queries
from ..navigation import find_message_by_uuid
from .. import load_latest_session

app = typer.Typer()
console = Console()


@app.command()
def reflog(limit: int = typer.Option(20, "--limit", "-n", help="Number of entries")):
    """Show all operations history (like git reflog)"""
    files = discover_current_project_files()
    if not files:
        console.print("No Claude sessions found", style="yellow")
        return

    jsonl_paths = [str(f) for f in files]
    results = reflog_queries.get_reflog(jsonl_paths, limit)

    if not results:
        console.print("No operations found", style="yellow")
        return

    for uuid, timestamp, tool, file_path, msg_type in results:
        # Format based on operation type
        if file_path:
            console.print(f"{str(uuid)[:8]} {tool}: {file_path}", style="green")
        elif tool:
            console.print(f"{str(uuid)[:8]} {tool}", style="yellow")
        else:
            console.print(f"{str(uuid)[:8]} {msg_type}", style="dim")


@app.command()
def show(uuid: str = typer.Argument(..., help="UUID to show")):
    """Show details of specific message (like git show)"""
    session = load_latest_session()
    if not session:
        console.print("No session found", style="red")
        return

    # Search through messages directly
    found_message = None
    for msg in session['messages']:
        if str(msg.get('uuid', '')).startswith(uuid):
            found_message = msg
            break

    if not found_message:
        console.print(f"UUID {uuid} not found", style="red")
        return

    # Display message details
    console.print(f"\n[bold]Message {uuid[:8]}...[/bold]")
    console.print(f"Type: {found_message.get('type', 'unknown')}", style="yellow")
    console.print(f"Time: {found_message.get('timestamp', 'unknown')}", style="dim")

    if 'toolUseResult' in found_message:
        result_data = found_message['toolUseResult']
        if isinstance(result_data, str):
            import json
            try:
                result = json.loads(result_data)
                console.print(f"Tool: {result.get('type', 'N/A')}", style="cyan")
                if 'filePath' in result:
                    console.print(f"File: {result['filePath']}", style="green")
                if 'content' in result:
                    console.print("\nFile Content:", style="bold")
                    content = result['content']
                    console.print(content[:500] + "..." if len(content) > 500 else content)
            except json.JSONDecodeError:
                console.print(f"Tool Result: {result_data}", style="cyan")