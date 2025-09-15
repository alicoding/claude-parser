#!/usr/bin/env python3
"""
CG checkout command - restore files from history
@SINGLE_SOURCE_TRUTH: Separated from cg.py for LOC compliance
@FRAMEWORK_FIRST: 100% delegation to operations module
"""
import typer
from typing import Optional
from pathlib import Path
from rich.console import Console

from .. import load_latest_session
from ..navigation import find_current_checkpoint
from ..operations import restore_file_from_jsonl, restore_folder_from_jsonl

app = typer.Typer()
console = Console()


@app.command()
def checkout(target: Optional[str] = typer.Argument(None)):
    """Restore files (like git checkout) - 0 tokens!"""
    session = load_latest_session()
    if not session:
        console.print("No session found", style="red")
        return

    jsonl_path = session.get('metadata', {}).get('transcript_path')
    if not jsonl_path:
        console.print("No transcript path found in session", style="red")
        return

    if not target:
        console.print("Usage: cg checkout <file> or cg checkout <uuid>", style="yellow")
        return

    checkpoint = find_current_checkpoint(session)
    if not checkpoint:
        console.print("No checkpoint found", style="yellow")
        return

    # Check if it's a folder checkout
    if target.endswith('/'):
        restored = restore_folder_from_jsonl(jsonl_path, checkpoint['uuid'], target)
        if restored:
            console.print(f"✓ Restored {len(restored)} files from {target}", style="green")
            for f in restored:
                console.print(f"  - {f}", style="dim")
        else:
            console.print(f"No files found in {target}", style="yellow")

    elif '.' in target or Path(target).exists():
        # Single file restoration
        file_path = str(Path(target).resolve())
        if restore_file_from_jsonl(jsonl_path, checkpoint['uuid'], file_path):
            console.print(f"✓ Restored {target} from checkpoint", style="green")
        else:
            console.print(f"No previous version of {target} found", style="yellow")
    else:
        # UUID checkout - TODO
        console.print(f"Restoring to UUID {target}...", style="cyan")
        console.print(f"Full UUID checkout in development", style="yellow")