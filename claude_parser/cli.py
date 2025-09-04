#!/usr/bin/env python3
"""Ultra-minimal CLI for claude-parser SDK - 95/5 principle."""

import orjson
from pathlib import Path
from typing import Optional

import typer
from rich import print

app = typer.Typer(help="Claude Parser - Parse & analyze Claude Code conversations")


@app.command()
def parse(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    stats: bool = typer.Option(False, "--stats", help="Show detailed statistics"),
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
            name = Path(project["original_path"]).name
            print(f"📂 {name} → {project['original_path']}")


@app.command()
def export(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    no_tools: bool = typer.Option(False, "--no-tools", help="Exclude tool messages"),
):
    """Export conversation for LlamaIndex/semantic search (JSON lines to stdout)."""
    from . import load
    from .memory import MemoryExporter

    conv = load(str(file))
    exporter = MemoryExporter(exclude_tools=no_tools)

    # Output JSON lines for piping
    for memory in exporter.export_as_dicts(conv):
        print(orjson.dumps(memory).decode())


@app.command()
def watch(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    after_uuid: Optional[str] = typer.Option(
        None, "--after-uuid", help="Resume from UUID checkpoint"
    ),
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


@app.command()
def operations(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    file_path: Optional[str] = typer.Option(
        None, "--file", help="Filter operations for specific file"
    ),
    after_uuid: Optional[str] = typer.Option(
        None, "--after-uuid", help="Show operations after UUID"
    ),
):
    """Show file operations in chronological order."""
    from . import load
    from .domain.services import FileNavigator

    try:
        conv = load(str(file))
        navigator = FileNavigator(conv.tool_uses)

        if file_path and after_uuid:
            ops = navigator.get_operations_after_uuid(after_uuid, file_path)
            print(f"📋 Operations on {file_path} after {after_uuid[:8]}...")
        elif file_path:
            ops = navigator.get_file_operations(file_path)
            print(f"📋 All operations on {file_path}")
        elif after_uuid:
            ops = navigator.get_operations_after_uuid(after_uuid)
            print(f"📋 All operations after {after_uuid[:8]}...")
        else:
            # Show summary
            summary = navigator.get_conversation_file_summary()
            print(
                f"📊 {summary['total_operations']} total operations on {summary['files_modified']} files"
            )
            for file_path, details in summary["file_details"].items():
                print(f"  📄 {file_path}: {details['operations_count']} operations")
            return

        for i, op in enumerate(ops, 1):
            file_op = navigator._extract_file_path(op)
            print(f"  {i:2d}. [{op.name}] {file_op} ({op.id[:8]})")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def timeline(
    project_path: Path = typer.Argument(
        None, help="Project path (auto-detects current dir if omitted)"
    ),
    checkout_uuid: Optional[str] = typer.Option(
        None, "--checkout", help="Checkout files at UUID"
    ),
    file_path: Optional[str] = typer.Option(
        None, "--file", help="Show timeline for specific file"
    ),
    steps: Optional[int] = typer.Option(
        None, "--steps", help="Navigate N steps from current/start"
    ),
    diff_uuid: Optional[str] = typer.Option(
        None, "--diff", help="Show diff for specific UUID"
    ),
    show_sessions: bool = typer.Option(
        False, "--sessions", help="Show multi-session summary"
    ),
):
    """Navigate file timeline using UUID checkpoints (like Ctrl+Z for Claude)."""
    from .domain.services import RealClaudeTimeline

    # Auto-detect project path if not provided
    if project_path is None:
        project_path = Path.cwd()

    try:
        timeline = RealClaudeTimeline(project_path)

        if diff_uuid:
            # Show what changed at specific UUID
            diff_info = timeline.get_operation_diff(diff_uuid)
            if diff_info:
                print(
                    f"🔍 Changes at {diff_uuid[:8]} ({diff_info['operation']} on {diff_info['file_path']})"
                )
                print("\n".join(diff_info["diff"]))
            else:
                print(f"❌ No operation found for UUID {diff_uuid[:8]}")

        elif checkout_uuid:
            # Restore files to specific UUID state
            state = timeline.checkout_by_uuid(checkout_uuid)
            if state:
                print(f"✅ Restored to UUID {checkout_uuid[:8]}")
                for file_path, info in state.items():
                    print(f"  📄 {file_path} ({len(info['content'])} chars)")
            else:
                print(f"❌ Cannot restore to UUID {checkout_uuid[:8]}")

        elif show_sessions:
            # Show multi-session summary
            summary = timeline.get_multi_session_summary()
            print(f"📊 Multi-Session Summary")
            print(f"   Sessions: {summary['total_sessions']}")
            print(f"   Operations: {summary['total_operations']}")
            print(f"   Project: {project_path}")

            for session_id, data in summary["sessions"].items():
                short_id = session_id[:8] if session_id != "unknown" else session_id
                files = ", ".join(Path(f).name for f in data["files_modified"])
                print(f"   📋 Session {short_id}: {data['operations']} ops → {files}")

        elif file_path and steps:
            # Navigate N steps in file history (using new query API)
            file_ops = [
                op
                for op in timeline.tool_operations
                if op.get("file_path", "").endswith(file_path)
            ]
            if file_ops and 0 < steps <= len(file_ops):
                target_op = file_ops[steps - 1]
                uuid = target_op.get("uuid")
                state = timeline.checkout_by_uuid(uuid) if uuid else None
                if state and file_path in state:
                    print(f"📍 Step {steps}/{len(file_ops)} for {file_path}")
                    print(f"🆔 UUID: {uuid[:8] if uuid else 'unknown'}")
                    content = state[file_path]["content"][:200].replace("\n", "\\n")
                    print(f"📝 Content: {content}...")
                else:
                    print(f"❌ Cannot restore step {steps} for {file_path}")
            else:
                print(f"❌ Invalid step {steps} for {file_path} (max: {len(file_ops)})")

        elif file_path:
            # Show file modification timeline
            file_ops = [
                op
                for op in timeline.tool_operations
                if op.get("file_path", "").endswith(file_path)
            ]
            print(f"📅 Timeline for {file_path} ({len(file_ops)} operations)")
            for i, op in enumerate(file_ops, 1):
                uuid = op.get("uuid", "unknown")
                tool = op.get("tool_name", "unknown")
                session = op.get("sessionId", "unknown")[:8]
                timestamp = op.get("timestamp", "")[:19]  # Just date/time
                print(f"  {i:2d}. {uuid[:8]} ({tool}) [{session}] {timestamp}")

        else:
            # Show all files and their modification counts with session info
            file_counts = {}
            session_counts = {}

            for op in timeline.tool_operations:
                if fp := op.get("file_path"):
                    filename = Path(fp).name
                    file_counts[filename] = file_counts.get(filename, 0) + 1
                if session := op.get("sessionId"):
                    session_counts[session[:8]] = session_counts.get(session[:8], 0) + 1

            print(
                f"📊 Timeline Summary ({len(timeline.tool_operations)} operations from {len(session_counts)} sessions)"
            )
            print(f"📂 Project: {project_path}")

            for filename, count in sorted(file_counts.items()):
                print(f"  📄 {filename}: {count} operations")

            if len(session_counts) > 1:
                print(f"🔀 Multi-session detected:")
                for session, count in session_counts.items():
                    print(f"  📋 Session {session}: {count} operations")

        timeline.clear_cache()

    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@app.command()
def navigate(
    file: Path = typer.Argument(..., help="Path to JSONL file"),
    file_path: str = typer.Argument(..., help="File to navigate"),
    current_uuid: Optional[str] = typer.Option(
        None, "--current", help="Current position UUID"
    ),
    back: bool = typer.Option(False, "--back", help="Go back one step"),
    forward: bool = typer.Option(False, "--forward", help="Go forward one step"),
):
    """Navigate file history like VSCode back/forward buttons."""
    from . import load
    from .domain.services import FileNavigator

    try:
        conv = load(str(file))
        navigator = FileNavigator(conv.tool_uses)

        if current_uuid:
            context = navigator.get_navigation_context(file_path, current_uuid)
            if "error" in context:
                print(f"❌ {context['error']}")
                return

            print(
                f"📍 {file_path} - Step {context['current_step']}/{context['total_steps']}"
            )
            print(f"🆔 Current: {context['current_uuid'][:8]}")

            if back and context["can_go_back"]:
                print(f"⬅️  Previous: {context['previous_uuid'][:8]}")
            elif forward and context["can_go_forward"]:
                print(f"➡️  Next: {context['next_uuid'][:8]}")
            else:
                print(
                    f"⬅️  Previous: {'None' if not context['can_go_back'] else context['previous_uuid'][:8]}"
                )
                print(
                    f"➡️  Next: {'None' if not context['can_go_forward'] else context['next_uuid'][:8]}"
                )
        else:
            # Show navigation timeline for file
            timeline_info = navigator.get_file_navigation_timeline(file_path)
            print(f"📅 Navigation timeline for {file_path}")
            for step in timeline_info:
                indicator = (
                    "🔹" if step["can_undo_to"] or step["can_redo_from"] else "🔸"
                )
                print(
                    f"  {indicator} Step {step['step']}: {step['operation']} ({step['uuid'][:8]})"
                )

    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
