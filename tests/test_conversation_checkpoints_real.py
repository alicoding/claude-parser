"""TDD tests using REAL Claude transcript data from actual project interactions.

Uses the real Claude project at:
- Project dir: /Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project
- Transcripts: /Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser-tests-fixtures-sample-project

This follows 95/5 principle by using real data instead of manufacturing fake data.
"""

import pytest
from pathlib import Path

from claude_parser.domain.services import ClaudeCodeTimeline
from claude_parser.infrastructure.discovery import ConfigurableProjectDiscovery


class TestConversationCheckpointsReal:
    """Test conversation checkpoints using actual Claude transcript data."""

    def test_real_project_discovery(self):
        """Test that we can discover the real test project."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        # Should find the actual Claude project
        found_project = discovery.find_current_project(real_project_path)
        assert found_project is not None

        # Should point to the encoded Claude projects directory
        expected_pattern = "claude-parser-tests-fixtures-sample-project"
        assert expected_pattern in str(found_project)

    def test_real_transcript_loading(self):
        """Test loading the real Claude transcript data."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        timeline = ClaudeCodeTimeline(real_project_path, discovery)

        # Should have loaded real events from actual Claude interactions
        assert len(timeline.raw_events) > 0

        # Should have real event structure
        for event in timeline.raw_events:
            if event.get("type") == "user":
                assert "uuid" in event
                assert "timestamp" in event
                assert "message" in event

    def test_find_last_user_message_real(self):
        """Test finding last user message from real Claude data."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        timeline = ClaudeCodeTimeline(real_project_path, discovery)
        last_user_message = timeline.find_last_user_message()

        # Should find a real user message from the actual conversation
        assert last_user_message is not None
        assert last_user_message["type"] == "user"
        assert "uuid" in last_user_message

    def test_operations_since_last_user_real(self):
        """Test getting operations since last user message with real data."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        timeline = ClaudeCodeTimeline(real_project_path, discovery)
        operations = timeline.get_operations_since_last_user_message()

        # Should get real operations from actual Claude interactions
        assert isinstance(operations, list)

    def test_status_since_last_user_real(self):
        """Test status summary with real Claude conversation data."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        timeline = ClaudeCodeTimeline(real_project_path, discovery)
        status = timeline.get_status_since_last_user_message()

        # Should have real status from actual conversation
        assert "operations_count" in status
        assert "files_changed" in status
        assert "last_user_message" in status

        # Values should be from real data
        assert isinstance(status["operations_count"], int)
        assert isinstance(status["files_changed"], int)

    def test_real_cwd_extraction(self):
        """Test that real cwd matches the actual project path."""
        real_project_path = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")
        discovery = ConfigurableProjectDiscovery()

        timeline = ClaudeCodeTimeline(real_project_path, discovery)

        # The extracted project working directory should match the real path
        assert timeline.project_path == real_project_path.resolve()

        # Should have extracted this from real JSONL cwd field
        assert timeline.project_path.exists()
        assert timeline.project_path.is_dir()
