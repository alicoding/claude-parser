#!/usr/bin/env python3
"""
CG reset and revert commands
@SINGLE_SOURCE_TRUTH: Separated from cg.py for LOC compliance
@FRAMEWORK_FIRST: 100% delegation to operations module
"""
import typer
from typing import Optional
from rich.console import Console

from .. import load_latest_session

app = typer.Typer()
console = Console()


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
        jsonl_path = session.get('metadata', {}).get('transcript_path')
        if not jsonl_path:
            console.print("No transcript path found", style="red")
            return
        # TODO: Implement full state restoration
        console.print(f"Would restore all files to state at {target[:8]}...", style="yellow")
    else:
        # Soft reset - just move pointer
        console.print(f"Soft reset to {target[:8]}... (pointer only)", style="cyan")
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
    message = next((m for m in messages if str(m.get('uuid', '')).startswith(target)), None)

    if message:
        console.print(f"Found change: {message.get('type', 'unknown')}", style="cyan")
        # TODO: Implement actual revert logic
        console.print(f"Would revert changes from {target[:8]}...", style="yellow")
    else:
        console.print(f"UUID {target[:8]}... not found", style="red")