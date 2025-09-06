"""Simplified TDD tests for conversation-aware status functionality.

Modern 95/5 approach with simple, working factories.
"""

import pytest
from pathlib import Path
import tempfile
import orjson

from claude_parser.domain.services import ClaudeCodeTimeline
from claude_parser.infrastructure.discovery import MockProjectDiscovery


def create_test_events(project_path: str):
    """Simple function to create test events - replaces complex factories."""
    return [
        {
            "type": "user",
            "uuid": "user-1",
            "timestamp": "2025-09-04T10:00:00Z",
            "message": {"content": "Create a hello world file"},
            "cwd": project_path
        },
        {
            "type": "assistant",
            "uuid": "asst-1",
            "timestamp": "2025-09-04T10:00:01Z",
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "Write",
                    "input": {
                        "file_path": f"{project_path}/hello.py",
                        "content": "print('Hello World')"
                    }
                }]
            },
            "cwd": project_path
        }
    ]


def create_test_project(events=None):
    """Simple function to create test project - eliminates tempfile duplication."""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir) / "project"
    project_path.mkdir()

    if events is None:
        events = create_test_events(str(project_path))

    # Create transcript
    transcript_path = project_path / "session.jsonl"
    with open(transcript_path, "w") as f:
        for event in events:
            f.write(orjson.dumps(event).decode() + "\n")

    # Create mock discovery
    mock_discovery = MockProjectDiscovery()
    mock_discovery.add_project("test", project_path, [transcript_path])

    return {
        "temp_dir": temp_dir,
        "project_path": project_path,
        "transcript_path": transcript_path,
        "mock_discovery": mock_discovery,
        "events": events
    }


class TestConversationCheckpoints:
    """Test conversation-aware status and diff functionality."""

    def test_find_last_user_message_simple(self):
        """Test finding the most recent user message (checkpoint)."""
        project_data = create_test_project()

        timeline = ClaudeCodeTimeline(
            project_data["project_path"],
            project_data["mock_discovery"]
        )

        last_user_message = timeline.find_last_user_message()

        assert last_user_message is not None
        assert last_user_message["type"] == "user"
        assert last_user_message["uuid"] == "user-1"

    def test_operations_since_last_user_message_simple(self):
        """Test getting operations since the last user message."""
        project_data = create_test_project()

        timeline = ClaudeCodeTimeline(
            project_data["project_path"],
            project_data["mock_discovery"]
        )

        # Since last user message, there should be 1 assistant operation
        operations_since_last = timeline.get_operations_since_last_user_message()
        assert len(operations_since_last) == 1
        assert operations_since_last[0]["tool_name"] == "Write"

    def test_status_summary_simple(self):
        """Test status summary showing changes since last user message."""
        project_data = create_test_project()

        timeline = ClaudeCodeTimeline(
            project_data["project_path"],
            project_data["mock_discovery"]
        )

        status = timeline.get_status_since_last_user_message()

        assert "operations_count" in status
        assert "files_changed" in status
        assert "last_user_message" in status
        assert status["operations_count"] == 1
        assert status["files_changed"] == 1

    def test_multiple_user_checkpoints(self):
        """Test with multiple user message checkpoints."""
        # Create events with multiple user messages
        project_path_str = "/test/project"
        events = [
            {
                "type": "user",
                "uuid": "user-1",
                "timestamp": "2025-09-04T10:00:00Z",
                "message": {"content": "Create file"},
                "cwd": project_path_str
            },
            {
                "type": "assistant",
                "uuid": "asst-1",
                "timestamp": "2025-09-04T10:00:01Z",
                "message": {
                    "content": [{
                        "type": "tool_use",
                        "name": "Write",
                        "input": {"file_path": f"{project_path_str}/hello.py", "content": "print('Hello')"}
                    }]
                },
                "cwd": project_path_str
            },
            {
                "type": "user",
                "uuid": "user-2",
                "timestamp": "2025-09-04T10:05:00Z",
                "message": {"content": "Edit file"},
                "cwd": project_path_str
            },
            {
                "type": "assistant",
                "uuid": "asst-2",
                "timestamp": "2025-09-04T10:05:01Z",
                "message": {
                    "content": [{
                        "type": "tool_use",
                        "name": "Edit",
                        "input": {
                            "file_path": f"{project_path_str}/hello.py",
                            "old_string": "print('Hello')",
                            "new_string": "print('Hello World')"
                        }
                    }]
                },
                "cwd": project_path_str
            }
        ]

        project_data = create_test_project(events)
        timeline = ClaudeCodeTimeline(
            project_data["project_path"],
            project_data["mock_discovery"]
        )

        # Should find user-2 as the last user message
        last_user_message = timeline.find_last_user_message()
        assert last_user_message["uuid"] == "user-2"

        # Should find 1 operation since user-2
        operations = timeline.get_operations_since_last_user_message()
        assert len(operations) == 1
        assert operations[0]["tool_name"] == "Edit"
