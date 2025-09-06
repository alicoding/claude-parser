#!/usr/bin/env python3
"""Ultra-minimal CLI for claude-parser SDK - 95/5 principle."""

from pathlib import Path
from typing import Optional

import typer
from rich import print

app = typer.Typer(help="Claude Parser - Parse & analyze Claude Code conversations")


@app.command()
def parse(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    stats: bool = typer.Option(False, "--stats", help="Show detailed statistics")
):
    """Parse a Claude Code JSONL file."""
    from . import load

    try:
        conv = load(str(file))

        if stats:
            from .analytics import ConversationAnalytics
            analytics = ConversationAnalytics(conv)
            stats_dict = analytics.get_statistics()
            print(stats_dict)
        else:
            print(f"📊 Messages: {len(conv.messages)}")
            print(f"👤 User: {len(conv.user_messages)}")
            print(f"🤖 Assistant: {len(conv.assistant_messages)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def find():
    """Find the current Claude transcript."""
    from . import find_current_transcript

    if transcript := find_current_transcript():
        print(f"📁 {transcript}")
    else:
        print("❌ No transcript found")
        raise typer.Exit(1)


@app.command()
def projects():
    """List all Claude projects."""
    from .discovery import list_all_projects

    projects = list_all_projects()
    if not projects:
        print("No projects found")
    else:
        for project in projects:
            # Extract name from path
            name = Path(project['original_path']).name
            print(f"📂 {name} → {project['original_path']}")


@app.command()
def export(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Exclude tool messages")
):
    """Export conversation for LlamaIndex/semantic search (JSON lines to stdout)."""
    from . import load
    from .memory import MemoryExporter

    conv = load(str(file))
    exporter = MemoryExporter(exclude_tools=no_tools)

    # Output JSON lines for piping
    for memory in exporter.export_as_dicts(conv):
        print(msgspec.json.encode(memory).decode())


@app.command()
def watch(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    after_uuid: Optional[str] = typer.Option(None, "--after-uuid", help="Resume from UUID checkpoint")
):
    """Watch a JSONL file for changes."""
    from .watch import watch as watch_sync

    def callback(conv, new_messages):
        print(f"📬 {len(new_messages)} new messages")
        if new_messages:
            for msg in new_messages[:3]:
                preview = msg.text_content[:50] if msg.text_content else "No content"
                print(f"  [{msg.type}] {preview}...")

    try:
        print(f"👀 Watching {file}...")
        watch_sync(str(file), callback, after_uuid=after_uuid)
    except KeyboardInterrupt:
        print("\n✋ Watch stopped")


if __name__ == "__main__":
    app()
