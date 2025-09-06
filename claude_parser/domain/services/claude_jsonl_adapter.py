"""
Claude JSONL Adapter - Transforms real Claude Code JSONL to Timeline format.
Pure function approach following 95/5 principle.
"""

from pathlib import Path
from typing import Dict, List

import jsonlines

from ...discovery import find_all_transcripts_for_cwd


def adapt_claude_jsonl_to_timeline_events(project_path: Path) -> List[Dict]:
    """
    Transform real Claude Code JSONL format to Timeline-compatible events.

    Real Claude structure:
    {
      "type": "assistant",
      "message": {
        "content": [
          {
            "type": "tool_use",
            "name": "Edit",
            "input": {"file_path": "...", "old_string": "...", "new_string": "..."}
          }
        ]
      },
      "uuid": "...",
      "sessionId": "...",
      "timestamp": "..."
    }

    Timeline expected format:
    {
      "uuid": "...",
      "tool_name": "Edit",
      "file_path": "...",
      "old_string": "...",
      "new_string": "...",
      "content": "..."
    }
    """
    # Auto-discover all JSONL files for this project
    transcript_paths = find_all_transcripts_for_cwd(project_path)

    if not transcript_paths:
        return []

    # Load all JSONL files (multi-session support)
    raw_events = []
    for transcript_path in transcript_paths:
        with jsonlines.open(transcript_path) as reader:
            session_events = list(reader)
            raw_events.extend(session_events)

    # Transform to Timeline format
    timeline_events = []

    for event in raw_events:
        # Skip non-assistant events
        if event.get("type") != "assistant":
            continue

        # Extract tool uses from message content
        message = event.get("message", {})
        content_items = message.get("content", [])

        for content_item in content_items:
            if (content_item.get("type") == "tool_use" and
                _is_file_operation(content_item)):

                # Build Timeline-compatible event
                tool_input = content_item.get("input", {})
                file_path = tool_input.get("file_path")

                # Convert absolute paths to just filename for Timeline compatibility
                if file_path:
                    file_path = Path(file_path).name

                timeline_event = {
                    "uuid": event.get("uuid"),
                    "sessionId": event.get("sessionId"),
                    "timestamp": event.get("timestamp"),
                    "parentUuid": event.get("parentUuid"),
                    "tool_name": content_item.get("name"),
                    "file_path": file_path,
                    "cwd": event.get("cwd", ""),
                }

                # Add tool-specific fields
                if content_item.get("name") == "Write":
                    timeline_event["content"] = tool_input.get("content", "")
                elif content_item.get("name") == "Edit":
                    timeline_event["old_string"] = tool_input.get("old_string", "")
                    timeline_event["new_string"] = tool_input.get("new_string", "")
                elif content_item.get("name") == "MultiEdit":
                    timeline_event["edits"] = tool_input.get("edits", [])

                timeline_events.append(timeline_event)

    # Sort chronologically across all sessions
    timeline_events.sort(key=lambda op: op.get("timestamp", ""))

    return timeline_events


def _is_file_operation(content_item: Dict) -> bool:
    """Check if content item is a file operation tool."""
    tool_name = content_item.get("name", "")
    return tool_name in ["Write", "Edit", "MultiEdit", "Read"]
