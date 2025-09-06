#!/usr/bin/env python3
"""
Git-like CLI for Claude Code operations - cg (claude-git) command.

Uses existing RealClaudeTimeline and discovery services with 95/5 principle.
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.table import Table
from rich.console import Console

from .domain.services import ClaudeCodeTimeline
from .infrastructure.discovery import ConfigurableProjectDiscovery
from .infrastructure.platform import get_claude_projects_dir
from .discovery import find_all_transcripts_for_cwd

app = typer.Typer(
    help="Git-like interface for Claude Code operations",
    add_completion=False,
    no_args_is_help=True
)

console = Console()


def get_timeline(project_path: Optional[Path] = None) -> ClaudeCodeTimeline:
    """Get timeline for project, with auto-detection."""
    if project_path is None:
        project_path = Path.cwd()

    try:
        return ClaudeCodeTimeline(project_path)
    except ValueError as e:
        print(f"❌ {e}")
        print(f"💡 Make sure you're in a directory that Claude Code has worked on")
        print(f"🔍 Check: ls ~/.claude/projects")
        raise typer.Exit(1)


@app.command()
def status(
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
    sessions: bool = typer.Option(False, "--sessions", help="Show detailed multi-session view"),
):
    """Show current project state and session information."""
    timeline = get_timeline(project_path)

    try:
        if sessions:
            # Detailed multi-session view
            summary = timeline.get_multi_session_summary()
            print(f"📊 Multi-Session Summary")
            print(f"   Sessions: {summary['total_sessions']}")
            print(f"   Operations: {summary['total_operations']}")
            print(f"   Project: {project_path or Path.cwd()}")
            print()

            for session_id, data in summary['sessions'].items():
                short_id = session_id[:8] if session_id != "unknown" else session_id
                files = ', '.join(Path(f).name for f in data['files_modified'])
                print(f"   📋 Session {short_id}: {data['operations']} ops → {files}")
        else:
            # Basic project status
            file_counts = {}
            session_counts = {}

            for op in timeline.tool_operations:
                if fp := op.get("file_path"):
                    filename = Path(fp).name
                    file_counts[filename] = file_counts.get(filename, 0) + 1
                if session := op.get("sessionId"):
                    session_counts[session[:8]] = session_counts.get(session[:8], 0) + 1

            print(f"📊 Timeline Summary ({len(timeline.tool_operations)} operations from {len(session_counts)} sessions)")
            print(f"📂 Project: {project_path or Path.cwd()}")

            for filename, count in sorted(file_counts.items()):
                print(f"  📄 {filename}: {count} operations")

            if len(session_counts) > 1:
                print(f"🔀 Multi-session detected:")
                for session, count in session_counts.items():
                    print(f"  📋 Session {session}: {count} operations")

    finally:
        timeline.clear_cache()


@app.command()
def log(
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
    file: Optional[str] = typer.Option(None, "--file", help="Show history for specific file"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Limit number of operations shown"),
    sessions: bool = typer.Option(False, "--sessions", help="Show session information"),
):
    """View operation history across all Claude Code sessions."""
    timeline = get_timeline(project_path)

    try:
        if file:
            # File-specific timeline
            file_ops = [op for op in timeline.tool_operations
                       if op.get('file_path', '').endswith(file)]

            print(f"📅 Timeline for {file} ({len(file_ops)} operations)")

            displayed_ops = file_ops[:limit] if limit else file_ops
            for i, op in enumerate(displayed_ops, 1):
                uuid = op.get('uuid', 'unknown')
                tool = op.get('tool_name', 'unknown')
                session = op.get('sessionId', 'unknown')[:8]
                timestamp = op.get('timestamp', '')[:19]  # Just date/time
                print(f"  {i:2d}. {uuid[:8]} ({tool}) [{session}] {timestamp}")

            if limit and len(file_ops) > limit:
                print(f"... and {len(file_ops) - limit} more operations")

        else:
            # All operations summary
            file_counts = {}
            session_counts = {}

            for op in timeline.tool_operations:
                if fp := op.get("file_path"):
                    filename = Path(fp).name
                    file_counts[filename] = file_counts.get(filename, 0) + 1
                if session := op.get("sessionId"):
                    session_counts[session[:8]] = session_counts.get(session[:8], 0) + 1

            print(f"📊 Timeline Summary ({len(timeline.tool_operations)} operations from {len(session_counts)} sessions)")
            print(f"📂 Project: {project_path or Path.cwd()}")

            for filename, count in sorted(file_counts.items()):
                print(f"  📄 {filename}: {count} operations")

            if len(session_counts) > 1:
                print(f"🔀 Multi-session detected:")
                for session, count in session_counts.items():
                    print(f"  📋 Session {session}: {count} operations")

            if sessions:
                print(f"\n📋 Recent Operations:")
                recent_ops = timeline.tool_operations[-10:] if len(timeline.tool_operations) > 10 else timeline.tool_operations
                for i, op in enumerate(recent_ops, 1):
                    uuid = op.get('uuid', 'unknown')[:8]
                    tool = op.get('tool_name', 'unknown')
                    filename = Path(op.get('file_path', '')).name if op.get('file_path') else 'unknown'
                    session = op.get('sessionId', 'unknown')[:8]
                    print(f"  {i:2d}. {uuid} ({tool}) {filename} [{session}]")

    finally:
        timeline.clear_cache()


@app.command()
def checkout(
    uuid: str = typer.Argument(..., help="UUID to checkout to"),
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
):
    """Restore files to exact state at specific UUID operation."""
    timeline = get_timeline(project_path)

    try:
        # Try with provided UUID (might be shortened)
        full_uuid = uuid
        if len(uuid) == 8:
            # Find full UUID from shortened version
            for op in timeline.tool_operations:
                if op.get('uuid', '').startswith(uuid):
                    full_uuid = op.get('uuid')
                    break

        state = timeline.checkout_by_uuid(full_uuid)
        if state:
            print(f"✅ Restored to UUID {uuid}")
            for file_path, info in state.items():
                print(f"  📄 {file_path} ({len(info['content'])} chars)")
        else:
            print(f"❌ Cannot restore to UUID {uuid}")
            print(f"💡 Use 'cg log' to see available UUIDs")

    finally:
        timeline.clear_cache()


@app.command()
def undo(
    steps: int = typer.Argument(1, help="Number of operations to undo"),
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
    to: Optional[str] = typer.Option(None, "--to", help="Undo to specific UUID"),
):
    """Go back N operations or to specific UUID."""
    timeline = get_timeline(project_path)

    try:
        if to:
            # Undo to specific UUID
            state = timeline.checkout_by_uuid(to)
            if state:
                print(f"✅ Restored to UUID {to[:8]}")
                for filename in state.keys():
                    print(f"  📄 {filename}")
            else:
                print(f"❌ Cannot restore to UUID {to[:8]}")
        else:
            # Undo N steps
            if steps <= 0:
                print(f"❌ Steps must be positive number")
                return

            # Get Edit/Write operations (skip Read operations)
            edit_operations = [op for op in timeline.tool_operations
                              if op.get("tool_name") in ["Write", "Edit", "MultiEdit"]]

            if steps > len(edit_operations):
                print(f"❌ Cannot undo {steps} steps. Only {len(edit_operations)} operations available.")
                return

            # Go back N steps from the end
            target_op = edit_operations[-(steps+1)] if steps < len(edit_operations) else edit_operations[0]
            target_uuid = target_op.get('uuid')

            if target_uuid:
                state = timeline.checkout_by_uuid(target_uuid)
                if state:
                    print(f"✅ Undid {steps} change(s)")
                    filename = Path(target_op.get("file_path", "")).name
                    print(f"📄 Restored: {filename}")
                    print(f"🆔 UUID: {target_uuid[:8]}")
                    print(f"🔧 Operation: {target_op.get('tool_name')}")
                else:
                    print(f"❌ Failed to undo to target operation")
            else:
                print(f"❌ Cannot find target operation")

    finally:
        timeline.clear_cache()


@app.command()
def show(
    uuid: str = typer.Argument(..., help="UUID to show details for"),
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
):
    """Show detailed information about a specific operation."""
    timeline = get_timeline(project_path)

    try:
        # Find the operation
        target_op = None
        full_uuid = uuid

        for op in timeline.tool_operations:
            op_uuid = op.get('uuid', '')
            if op_uuid == uuid or op_uuid.startswith(uuid):
                target_op = op
                full_uuid = op_uuid
                break

        if not target_op:
            print(f"❌ Operation {uuid} not found")
            print(f"💡 Use 'cg log' to see available operations")
            return

        print(f"🔍 Operation {uuid}")
        print(f"   Type: {target_op.get('tool_name', 'unknown')}")
        print(f"   File: {Path(target_op.get('file_path', '')).name}")
        print(f"   Session: {target_op.get('sessionId', 'unknown')[:8]}")
        print(f"   Timestamp: {target_op.get('timestamp', '')[:19]}")

        # Show operation details
        tool_input = target_op.get('tool_input', {})
        if target_op.get('tool_name') == 'Edit':
            old_str = tool_input.get('old_string', '')[:50]
            new_str = tool_input.get('new_string', '')[:50]
            print(f"   Changes: {old_str} → {new_str}")
        elif target_op.get('tool_name') == 'Write':
            content = tool_input.get('content', '')[:100]
            print(f"   Content: {content}...")

    finally:
        timeline.clear_cache()


@app.command()
def diff(
    project_path: Optional[Path] = typer.Argument(None, help="Project path (auto-detects if omitted)"),
    uuid_range: Optional[str] = typer.Option(None, "--range", help="Compare UUIDs (uuid1..uuid2)"),
    uuid: Optional[str] = typer.Option(None, "--uuid", help="Show diff for specific UUID"),
):
    """Show differences between operations or current vs previous."""
    timeline = get_timeline(project_path)

    try:
        if uuid:
            # Show what changed at specific UUID
            diff_info = timeline.get_operation_diff(uuid)
            if diff_info:
                print(f"🔍 Changes at {uuid[:8]} ({diff_info['operation']} on {diff_info['file_path']})")
                for line in diff_info['diff']:
                    print(line)
            else:
                print(f"❌ No operation found for UUID {uuid[:8]}")
        elif uuid_range:
            # Compare two UUIDs
            if '..' in uuid_range:
                uuid1, uuid2 = uuid_range.split('..', 1)
                from_state = timeline.checkout_by_uuid(uuid1)
                to_state = timeline.checkout_by_uuid(uuid2)

                if from_state and to_state:
                    print(f"🔍 Comparing {uuid1[:8]}..{uuid2[:8]}")
                    # Simple comparison - could be enhanced
                    from_files = set(from_state.keys())
                    to_files = set(to_state.keys())

                    added = to_files - from_files
                    removed = from_files - to_files
                    modified = from_files & to_files

                    if added:
                        print(f"➕ Added: {', '.join(added)}")
                    if removed:
                        print(f"➖ Removed: {', '.join(removed)}")
                    if modified:
                        print(f"📝 Modified: {', '.join(modified)}")
                else:
                    print(f"❌ Cannot compare {uuid1[:8]} and {uuid2[:8]}")
            else:
                print(f"❌ Range format should be: uuid1..uuid2")
        else:
            # Show recent changes (last operation)
            edit_operations = [op for op in timeline.tool_operations
                              if op.get("tool_name") in ["Write", "Edit", "MultiEdit"]]
            if edit_operations:
                last_op = edit_operations[-1]
                uuid = last_op.get('uuid')
                if uuid:
                    diff_info = timeline.get_operation_diff(uuid)
                    if diff_info:
                        print(f"🔍 Recent changes ({diff_info['operation']} on {Path(diff_info['file_path']).name})")
                        for line in diff_info['diff'][:10]:  # Limit output
                            print(line)
                    else:
                        print(f"❌ Cannot show diff for recent operation")
                else:
                    print(f"❌ No recent operations found")
            else:
                print(f"📭 No operations found")

    finally:
        timeline.clear_cache()


@app.command()
def timeline(
    project_path: Optional[Path] = typer.Argument(
        None, help="Project path (auto-detects if omitted)"
    ),
    since: bool = typer.Option(
        False, "--since", help="Show changes since last user message (checkpoint view)"
    ),
    sessions: bool = typer.Option(
        False, "--sessions", help="Show multi-session timeline"
    ),
):
    """Show conversation timeline with git-like visualization."""
    # Skip execution in test mode
    import os
    if os.environ.get("CLAUDE_PARSER_TEST_MODE"):
        return

    timeline_service = get_timeline(project_path)

    try:
        from .domain.services import TimelineVisualizer
        visualizer = TimelineVisualizer()

        if sessions:
            # Multi-session view
            output = visualizer.create_session_timeline(timeline_service.conversations)
            print(output)
        elif since:
            # Checkpoint view - since last user message
            newest_conv = timeline_service.conversations[0]
            last_user = timeline_service.find_last_user_message()
            if last_user:
                output = visualizer.create_checkpoint_view(newest_conv, last_user["timestamp"])
                print(output)
            else:
                print("❌ No user messages found for checkpoint view")
        else:
            # Full conversation timeline
            newest_conv = timeline_service.conversations[0]
            output = visualizer.create_conversation_timeline(newest_conv)
            print(output)

    finally:
        timeline_service.clear_cache()


if __name__ == "__main__":
    app()
