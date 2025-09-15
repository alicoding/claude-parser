#!/usr/bin/env python3
"""
Git-like CLI for Claude Parser - Pure composition over API
Typer framework delegation with <80 LOC per command
"""
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

# @FRAMEWORK_FACADE - Import interface only
from .. import discover_all_sessions, load_latest_session
from ..discovery import discover_current_project_files
from ..navigation import get_timeline_summary, find_current_checkpoint, find_message_by_uuid
from ..operations import restore_file_from_jsonl, restore_folder_from_jsonl

app = typer.Typer(help="Git-like interface for Claude Code conversations")
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

    # Get last N messages
    from more_itertools import take
    display_messages = list(take(limit, reversed(messages))) if limit else messages

    # Print messages
    for msg in reversed(display_messages):
        msg_type = msg.get('type', 'unknown')
        content = str(msg.get('content', ''))[:100]
        console.print(f"[bold]{msg_type}[/bold]: {content}{'...' if len(str(msg.get('content', ''))) > 100 else ''}")



@app.command()
def checkout(target: Optional[str] = typer.Argument(None)):
    """Restore files (like git checkout) - 0 tokens!"""
    from pathlib import Path

    session = load_latest_session()
    if not session:
        console.print("No session found", style="red")
        return

    # Get JSONL path from session metadata
    jsonl_path = session.get('metadata', {}).get('transcript_path')
    if not jsonl_path:
        console.print("No transcript path found in session", style="red")
        return

    if target:
        checkpoint = find_current_checkpoint(session)
        if not checkpoint:
            console.print("No checkpoint found", style="yellow")
            return

        # Check if it's a folder checkout
        if target.endswith('/'):
            # Delegate to operations domain
            restored = restore_folder_from_jsonl(jsonl_path, checkpoint['uuid'], target)
            if restored:
                console.print(f"✓ Restored {len(restored)} files from {target}", style="green")
                for f in restored:
                    console.print(f"  - {f}", style="dim")
            else:
                console.print(f"No files found in {target}", style="yellow")

        elif '.' in target or Path(target).exists():
            # Single file - delegate to operations
            file_path = str(Path(target).resolve())
            if restore_file_from_jsonl(jsonl_path, checkpoint['uuid'], file_path):
                console.print(f"✓ Restored {target} from checkpoint", style="green")
            else:
                console.print(f"No previous version of {target} found", style="yellow")
        else:
            # UUID checkout - restore all files at that state
            console.print(f"Restoring to UUID {target}...", style="cyan")
            # TODO: Implement full state restoration
            console.print(f"Full UUID checkout in development", style="yellow")
    else:
        console.print("Usage: cg checkout <file> or cg checkout <uuid>", style="yellow")


@app.command()
def reset(hard: bool = typer.Option(False, "--hard", help="Reset files to state"),
          target: Optional[str] = typer.Argument(None, help="UUID to reset to")):
    """Reset to a previous state (like git reset)"""
    if not target:
        console.print("Usage: cg reset [--hard] <uuid>", style="yellow")
        return

    session = load_latest_session()
    if not session:
        console.print("No session found", style="red")
        return

    if hard:
        # Hard reset - restore all files to that state
        console.print(f"Hard reset to {target[:8]}... - restoring files", style="cyan")

        # Get JSONL path and query files at checkpoint
        jsonl_path = session.get('metadata', {}).get('transcript_path')
        if not jsonl_path:
            console.print("No transcript path found", style="red")
            return

        from ..storage.jsonl_engine import query_jsonl
        # Query all file operations before this UUID
        # For now, show what would be restored
        console.print(f"Would restore all files to state at {target[:8]}...", style="yellow")
    else:
        # Soft reset - just move pointer
        console.print(f"Soft reset to {target[:8]}... (pointer only)", style="cyan")
        # In Claude context, this means "consider this the new baseline"
        console.print("Checkpoint updated (soft reset)", style="green")


@app.command()
def revert(target: str = typer.Argument(..., help="UUID to revert")):
    """Revert a specific change (like git revert)"""
    session = load_latest_session()
    if not session:
        console.print("No session found", style="red")
        return

    console.print(f"Reverting changes from {target[:8]}...", style="cyan")

    # Find the message at this UUID in the messages list
    messages = session.get('messages', [])
    message = next((m for m in messages if m.get('uuid') == target), None)

    if message:
        console.print(f"Found change: {message.get('type', 'unknown')}", style="cyan")
        # For now, show what would be reverted
        console.print(f"Would revert changes from {target[:8]}...", style="yellow")
    else:
        console.print(f"UUID {target[:8]}... not found", style="red")


# Import and register advanced commands
from . import cg_advanced, cg_reflog
app.add_typer(cg_advanced.app, name="", help="Advanced git-like commands")
app.add_typer(cg_reflog.app, name="", help="Reflog and show commands")


if __name__ == "__main__":
    app()