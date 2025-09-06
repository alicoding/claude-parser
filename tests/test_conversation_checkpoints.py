"""TDD tests for conversation-aware status functionality.

Tests the concept of 'since last user message' inspired by Aider's approach.
Each user message is a natural checkpoint boundary for showing file changes.

Modern 95/5 approach using factories - eliminates test duplication.
"""

import pytest
from pathlib import Path

from claude_parser.domain.services import ClaudeCodeTimeline
from tests.factories import ProjectFactory, TranscriptFactory, UserMessageFactory, AssistantMessageFactory


@pytest.fixture
def project_with_checkpoints():
    """Standard project fixture with conversation checkpoints - replaces 20+ lines per test."""
    return ProjectFactory.create_temp_project()


@pytest.fixture
def timeline_service(project_with_checkpoints):
    """Timeline service fixture - eliminates service setup duplication."""
    project_data = project_with_checkpoints
    mock_discovery = ProjectFactory.create_mock_discovery(project_data)
    return ClaudeCodeTimeline(project_data["project_path"], mock_discovery)


class TestConversationCheckpoints:
    """Test conversation-aware status and diff functionality."""

    def test_find_last_user_message(self, timeline_service, project_with_checkpoints):
        """Test finding the most recent user message (checkpoint)."""
        # Framework handles all setup, test focuses on behavior
        last_user_message = timeline_service.find_last_user_message()

        assert last_user_message is not None
        assert last_user_message["type"] == "user"

    def test_operations_since_last_user_message(self, timeline_service):
        """Test getting operations since the last user message."""
        # Default factory creates scenario where last message is user message
        operations_since_last = timeline_service.get_operations_since_last_user_message()
        assert isinstance(operations_since_last, list)

    def test_operations_since_specific_user_message(self, project_with_checkpoints):
        """Test getting operations since a specific user message checkpoint."""
        project_data = project_with_checkpoints

        # Create custom scenario with specific user message pattern
        events = [
            UserMessageFactory(uuid="user-1", timestamp="2025-09-04T10:00:00Z", cwd=str(project_data["project_path"])),
            AssistantMessageFactory(uuid="asst-1", timestamp="2025-09-04T10:00:01Z", cwd=str(project_data["project_path"])),
            UserMessageFactory(uuid="user-2", timestamp="2025-09-04T10:05:00Z", cwd=str(project_data["project_path"])),
            AssistantMessageFactory(uuid="asst-2", timestamp="2025-09-04T10:05:01Z", cwd=str(project_data["project_path"]))
        ]

        # Create new project with specific events
        custom_project = ProjectFactory.create_temp_project(events=events)
        mock_discovery = ProjectFactory.create_mock_discovery(custom_project)
        timeline = ClaudeCodeTimeline(custom_project["project_path"], mock_discovery)

        # Since user-2 message, there should be 1 operation
        operations_since_user2 = timeline.get_operations_since_user_message("user-2")
        assert len(operations_since_user2) == 1

    def test_status_summary_since_last_user(self, timeline_service):
        """Test status summary showing changes since last user message."""
        status = timeline_service.get_status_since_last_user_message()

        # Verify status structure
        assert "operations_count" in status
        assert "files_changed" in status
        assert "last_user_message" in status

    def test_conversation_with_no_user_messages(self):
        """Test handling conversation with no user messages."""
        # Only assistant messages using factory
        events = [
            AssistantMessageFactory(
                uuid="asst-1",
                timestamp="2025-09-04T10:00:00Z",
                message={"content": [{"type": "text", "text": "Hello"}]}
            )
        ]

        project_data = ProjectFactory.create_temp_project(events=events)
        mock_discovery = ProjectFactory.create_mock_discovery(project_data)
        timeline = ClaudeCodeTimeline(project_data["project_path"], mock_discovery)

        # Should handle gracefully
        last_user_message = timeline.find_last_user_message()
        assert last_user_message is None

    def test_multi_session_user_message_tracking(self):
        """Test tracking user messages across multiple transcript files."""
        project_data = ProjectFactory.create_temp_project()

        # Create second transcript with later timestamp
        session2_events = [
            UserMessageFactory(
                uuid="user-2",
                timestamp="2025-09-04T10:00:00Z",
                message={"content": "Continue project"},
                cwd=str(project_data["project_path"])
            )
        ]

        # Add second transcript file
        transcript2 = project_data["project_path"] / "session2.jsonl"
        from tests.factories.conversation import create_conversation_transcript
        transcript2.write_text(create_conversation_transcript(session2_events))

        # Update mock discovery to include both transcripts
        mock_discovery = ProjectFactory.create_mock_discovery(project_data)
        mock_discovery.add_project(
            "test",
            project_data["project_path"],
            [project_data["transcript_path"], transcript2]
        )

        timeline = ClaudeCodeTimeline(project_data["project_path"], mock_discovery)

        # Should find the most recent user message across all sessions
        last_user_message = timeline.find_last_user_message()
        assert last_user_message is not None
        assert last_user_message["uuid"] == "user-2"

    def test_status_with_operations_since_user_message(self, project_with_checkpoints):
        """Test status when there ARE operations since last user message."""
        project_data = project_with_checkpoints

        # Add an operation after the last user message using factory
        extended_events = project_data["events"] + [
            UserMessageFactory(
                uuid="user-3",
                timestamp="2025-09-04T10:10:00Z",
                message={"content": "What files have we changed?"},
                cwd=str(project_data["project_path"])
            ),
            AssistantMessageFactory(
                uuid="asst-3",
                timestamp="2025-09-04T10:10:01Z",
                message={
                    "content": [{
                        "type": "tool_use",
                        "name": "Write",
                        "input": {
                            "file_path": str(project_data["project_path"] / "config.py"),
                            "content": "CONFIG = {}"
                        }
                    }]
                },
                cwd=str(project_data["project_path"])
            )
        ]

        extended_project = ProjectFactory.create_temp_project(events=extended_events)
        mock_discovery = ProjectFactory.create_mock_discovery(extended_project)
        timeline = ClaudeCodeTimeline(extended_project["project_path"], mock_discovery)

        status = timeline.get_status_since_last_user_message()

        # Should show 1 operation since last user message
        assert status["operations_count"] == 1
        assert status["files_changed"] == 1
