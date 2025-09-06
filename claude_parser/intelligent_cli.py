"""
Intelligent CLI - Zero-config "Ctrl-Z for Claude" commands.
User doesn't specify paths/files - we figure it out using SOLID design.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
from rich import print
from rich.table import Table

from .discovery import find_all_transcripts_for_cwd
from .domain.services import RealClaudeTimeline


app = typer.Typer(help="Intelligent Claude Undo - Zero-config file restoration")


class IntelligentClaudeUndo:
    """Smart undo system that figures out context automatically."""

    def __init__(self, project_path: Optional[Path] = None):
        self.project_path = project_path or Path.cwd()
        self.timeline = None
        self._load_timeline()

    def _load_timeline(self):
        """Auto-detect and load timeline for current context."""
        try:
            self.timeline = RealClaudeTimeline(self.project_path)
        except ValueError:
            raise typer.Exit(f"❌ No Claude Code sessions found in {self.project_path}")

    def get_recent_changes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent file changes across all sessions."""
        # Filter to only file-modifying operations
        file_ops = [op for op in self.timeline.tool_operations
                   if op.get("tool_name") in ["Write", "Edit", "MultiEdit"]]

        # Sort by timestamp (most recent first)
        recent_ops = sorted(file_ops, key=lambda op: op.get("timestamp", ""), reverse=True)

        return recent_ops[:limit]

    def smart_undo(self, steps: int = 1) -> Dict[str, Any]:
        """Intelligent undo - go back N meaningful changes."""
        recent_changes = self.get_recent_changes(steps + 10)  # Get extra for context

        if not recent_changes:
            return {"error": "No changes to undo"}

        if steps > len(recent_changes):
            steps = len(recent_changes)

        # Target the Nth most recent change
        target_operation = recent_changes[steps - 1]
        target_uuid = target_operation.get("uuid")

        if not target_uuid:
            return {"error": "Cannot find operation to undo to"}

        # Restore to that state
        state = self.timeline.checkout_by_uuid(target_uuid)

        return {
            "success": True,
            "target_uuid": target_uuid,
            "target_operation": target_operation,
            "restored_files": list(state.keys()) if state else [],
            "steps_back": steps
        }

    def show_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Show recent history in user-friendly format."""
        recent_changes = self.get_recent_changes(limit)

        history = []
        for i, op in enumerate(recent_changes, 1):
            file_path = op.get("file_path", "")
            filename = Path(file_path).name if file_path else "unknown"

            history.append({
                "step": i,
                "uuid": op.get("uuid", "")[:8],
                "operation": op.get("tool_name", ""),
                "file": filename,
                "session": op.get("sessionId", "")[:8],
                "timestamp": op.get("timestamp", "")[:19],  # Just date/time
                "full_uuid": op.get("uuid", "")
            })

        return history

    def detect_modified_files(self) -> Dict[str, int]:
        """Auto-detect which files were recently modified."""
        file_counts = {}

        for op in self.timeline.tool_operations:
            if file_path := op.get("file_path"):
                filename = Path(file_path).name
                file_counts[filename] = file_counts.get(filename, 0) + 1

        # Sort by modification count (most modified first)
        return dict(sorted(file_counts.items(), key=lambda x: x[1], reverse=True))

    def cleanup(self):
        """Clean up resources."""
        if self.timeline:
            self.timeline.clear_cache()


@app.command("undo")
def undo(
    steps: int = typer.Argument(1, help="Number of changes to undo (default: 1)"),
    to_uuid: Optional[str] = typer.Option(None, "--to", help="Undo to specific UUID"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be undone without doing it"),
):
    """Intelligent undo - go back N changes without specifying files or paths."""

    undo_system = IntelligentClaudeUndo()

    try:
        if to_uuid:
            # Specific UUID restore
            state = undo_system.timeline.checkout_by_uuid(to_uuid)
            if state:
                if not dry_run:
                    print(f"✅ Restored to UUID {to_uuid[:8]}")
                    for filename in state.keys():
                        print(f"  📄 {filename}")
                else:
                    print(f"🔍 Would restore to UUID {to_uuid[:8]}")
                    for filename in state.keys():
                        print(f"  📄 {filename}")
            else:
                print(f"❌ Cannot restore to UUID {to_uuid[:8]}")
        else:
            # Smart undo by steps
            result = undo_system.smart_undo(steps)

            if result.get("success"):
                target_op = result["target_operation"]
                filename = Path(target_op.get("file_path", "")).name

                if not dry_run:
                    print(f"✅ Undid {steps} change(s)")
                    print(f"📄 Restored: {filename}")
                    print(f"🆔 UUID: {result['target_uuid'][:8]}")
                    print(f"🔧 Operation: {target_op.get('tool_name')}")
                else:
                    print(f"🔍 Would undo {steps} change(s)")
                    print(f"📄 Would restore: {filename}")
                    print(f"🆔 Target UUID: {result['target_uuid'][:8]}")
            else:
                print(f"❌ {result.get('error', 'Unknown error')}")

    finally:
        undo_system.cleanup()


@app.command("history")
def history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number of recent changes to show"),
    file: Optional[str] = typer.Option(None, "--file", help="Show history for specific file only"),
):
    """Show recent change history across all sessions."""

    undo_system = IntelligentClaudeUndo()

    try:
        history_items = undo_system.show_history(limit)

        if file:
            # Filter to specific file
            history_items = [item for item in history_items if item["file"] == file]

        if not history_items:
            print("📭 No recent changes found")
            return

        # Create rich table
        table = Table(title=f"Recent Claude Changes ({'All Files' if not file else file})")
        table.add_column("Step", style="cyan", width=4)
        table.add_column("UUID", style="blue", width=8)
        table.add_column("Operation", style="green", width=10)
        table.add_column("File", style="yellow", width=20)
        table.add_column("Session", style="magenta", width=8)
        table.add_column("Timestamp", style="dim", width=19)

        for item in history_items:
            table.add_row(
                str(item["step"]),
                item["uuid"],
                item["operation"],
                item["file"],
                item["session"],
                item["timestamp"]
            )

        print(table)
        print(f"\n💡 Use 'claude undo {history_items[0]['step']}' to restore to step {history_items[0]['step']}")

    finally:
        undo_system.cleanup()


@app.command("status")
def status():
    """Show intelligent status - what files changed, which sessions, etc."""

    undo_system = IntelligentClaudeUndo()

    try:
        # Multi-session summary
        summary = undo_system.timeline.get_multi_session_summary()

        print(f"📊 Claude Project Status")
        print(f"📂 Project: {undo_system.project_path}")
        print(f"🔀 Sessions: {summary['total_sessions']}")
        print(f"⚡ Operations: {summary['total_operations']}")

        # Recent changes
        recent = undo_system.get_recent_changes(3)
        if recent:
            print(f"\n📝 Recent Changes:")
            for i, op in enumerate(recent, 1):
                filename = Path(op.get("file_path", "")).name
                tool = op.get("tool_name", "")
                timestamp = op.get("timestamp", "")[:16]  # Just date/hour
                print(f"  {i}. {tool} {filename} ({timestamp})")

        # Modified files
        file_counts = undo_system.detect_modified_files()
        if file_counts:
            print(f"\n📄 Modified Files:")
            for filename, count in list(file_counts.items())[:5]:  # Top 5
                print(f"  {filename}: {count} changes")

        # Multi-session detection
        if summary['total_sessions'] > 1:
            print(f"\n🔀 Multi-session Project:")
            for session_id, data in summary['sessions'].items():
                short_id = session_id[:8]
                files = ', '.join(Path(f).name for f in data['files_modified'])
                print(f"  📋 {short_id}: {data['operations']} ops → {files}")

    finally:
        undo_system.cleanup()


if __name__ == "__main__":
    app()
