#!/usr/bin/env python3
"""
Basic CG commands - status and log
@SINGLE_SOURCE_TRUTH: Separated from cg.py for LOC compliance
@FRAMEWORK_FIRST: 100% delegation to existing modules
"""
import typer
from rich.console import Console
from rich.table import Table
from more_itertools import take

from .. import discover_all_sessions, load_latest_session
from ..discovery import discover_current_project_files

app = typer.Typer()
console = Console()


@app.command()
def status():
    """Show current session and project status"""
    sessions = discover_all_sessions()
    if not sessions:
        console.print("No Claude sessions found", style="yellow")
        return
    current_session, files = load_latest_session(), discover_current_project_files()
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Status")
    table.add_column("Info")
    table.add_row("Sessions", f"{len(sessions)} found")
    table.add_row("Files", f"{len(files)} Claude files")
    if current_session:
        # Simple message count from dict
        messages = current_session.get('messages', [])
        table.add_row("Messages", f"{len(messages)} messages")

        # Find last file operation manually
        file_ops = [m for m in messages if m.get('toolUseResult') and 'filePath' in str(m.get('toolUseResult', {}))]
        if file_ops:
            last_op = file_ops[-1]
            table.add_row("Last file op", f"UUID: {last_op.get('uuid', 'unknown')[:8]}...")
        else:
            table.add_row("File ops", "No file operations found")
    console.print(table)


@app.command()
def log(limit: int = typer.Option(10, "--limit", "-n", help="Number of messages")):
    """Show message history"""
    current_session = load_latest_session()
    if not current_session:
        console.print("No current session found", style="yellow")
        return

    # Handle dict-based session
    messages = current_session.get('messages', [])
    if not messages:
        console.print("No messages found in session", style="yellow")
        return

    # Get last N messages using more-itertools
    display_messages = list(take(limit, reversed(messages))) if limit else messages

    # Print messages
    for msg in reversed(display_messages):
        msg_type = msg.get('type', 'unknown')
        content = str(msg.get('content', ''))[:100]
        console.print(f"[bold]{msg_type}[/bold]: {content}{'...' if len(str(msg.get('content', ''))) > 100 else ''}")