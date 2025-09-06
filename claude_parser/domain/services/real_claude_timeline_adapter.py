"""
Real Claude Timeline - SOLID extension of existing Timeline.
Uses adapter pattern to transform real Claude JSONL data.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .claude_jsonl_adapter import adapt_claude_jsonl_to_timeline_events
from .timeline_service import Timeline


class RealClaudeTimeline(Timeline):
    """Timeline that works with real Claude Code JSONL data."""

    def __init__(self, project_path: Path):
        """Initialize timeline from Claude Code project path."""
        # Transform real Claude JSONL to Timeline format
        timeline_events = adapt_claude_jsonl_to_timeline_events(project_path)

        if not timeline_events:
            raise ValueError(f"No Claude Code transcripts found for {project_path}")

        # Create temporary directory with transformed events
        temp_dir = Path(tempfile.mkdtemp())
        temp_jsonl = temp_dir / "events.jsonl"

        import jsonlines
        with jsonlines.open(temp_jsonl, mode='w') as writer:
            writer.write_all(timeline_events)

        # Initialize parent Timeline with transformed data
        super().__init__(temp_dir)

        # Store original events for additional functionality
        self.tool_operations = timeline_events

    def get_session_operations(self, session_id: str) -> List[Dict]:
        """Get all operations from a specific session."""
        return [op for op in self.tool_operations
                if op.get("sessionId") == session_id]

    def get_multi_session_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions and their operations."""
        sessions = {}

        for operation in self.tool_operations:
            session_id = operation.get("sessionId", "unknown")
            if session_id not in sessions:
                sessions[session_id] = {
                    "operations": 0,
                    "files_modified": set(),
                    "first_timestamp": operation.get("timestamp"),
                    "last_timestamp": operation.get("timestamp"),
                }

            sessions[session_id]["operations"] += 1
            if file_path := operation.get("file_path"):
                sessions[session_id]["files_modified"].add(file_path)

            # Update timestamps
            timestamp = operation.get("timestamp", "")
            if timestamp < sessions[session_id]["first_timestamp"]:
                sessions[session_id]["first_timestamp"] = timestamp
            if timestamp > sessions[session_id]["last_timestamp"]:
                sessions[session_id]["last_timestamp"] = timestamp

        # Convert sets to lists for JSON serialization
        for session_data in sessions.values():
            session_data["files_modified"] = list(session_data["files_modified"])

        return {
            "total_sessions": len(sessions),
            "total_operations": len(self.tool_operations),
            "sessions": sessions
        }
