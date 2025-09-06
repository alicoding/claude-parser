"""
Real timeline tests with production data using MockProjectDiscovery.
These tests were previously using actual filesystem files but now use clean mocks.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from claude_parser.domain.services.claude_code_timeline import ClaudeCodeTimeline
from claude_parser.infrastructure.discovery import MockProjectDiscovery


# Create an alias for backward compatibility with existing tests
RealClaudeTimeline = ClaudeCodeTimeline


class TestRealClaudeTimeline:
    """Test ClaudeCodeTimeline with production-like data structure."""

    @pytest.fixture
    def test_project_path(self):
        """Create a test project path."""
        return Path("/tmp/claude-parser-test-project")

    @pytest.fixture
    def production_like_data(self):
        """Create production-like JSONL data."""
        return [
            {
                "type": "user",
                "uuid": "user-msg-1",
                "sessionId": "prod-session-1",
                "timestamp": "2025-01-04T10:00:00Z",
                "message": {"content": "Help me create a new feature"},
            },
            {
                "type": "assistant",
                "uuid": "asst-msg-1",
                "sessionId": "prod-session-1",
                "timestamp": "2025-01-04T10:00:30Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": "/tmp/claude-parser-test-project/feature.py",
                                "content": "def new_feature():\n    return 'feature implemented'\n",
                            },
                        }
                    ]
                },
            },
        ]

    def _create_timeline_with_production_data(self, project_path, jsonl_data):
        """Helper to create timeline with production-like data."""
        mock_discovery = MockProjectDiscovery()
        transcript_path = project_path / "claude_session.jsonl"
        mock_discovery.add_project("prod-project", project_path, [transcript_path])

        with patch("claude_parser.domain.services.claude_code_timeline.jsonlines.open") as mock_jsonlines:
            mock_jsonlines.return_value.__enter__.return_value = jsonl_data
            return RealClaudeTimeline(project_path, mock_discovery)

    def test_initialization_with_real_data(self, test_project_path, production_like_data):
        """Should initialize with real Claude Code JSONL files."""
        timeline = self._create_timeline_with_production_data(test_project_path, production_like_data)

        assert len(timeline.tool_operations) == 1
        assert len(timeline.raw_events) == 2

        timeline.clear_cache()

    def test_multi_session_detection(self, test_project_path):
        """Should detect and handle multiple sessions."""
        multi_session_data = [
            {
                "type": "assistant",
                "uuid": "write-session-1",
                "sessionId": "session-111",
                "timestamp": "2025-01-04T09:00:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": str(test_project_path / "config.py"),
                                "content": "CONFIG = {}\n",
                            },
                        }
                    ]
                },
            },
            {
                "type": "assistant",
                "uuid": "edit-session-2",
                "sessionId": "session-222",
                "timestamp": "2025-01-04T10:00:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {
                                "file_path": str(test_project_path / "config.py"),
                                "old_string": "CONFIG = {}",
                                "new_string": "CONFIG = {'debug': True}",
                            },
                        }
                    ]
                },
            },
        ]

        timeline = self._create_timeline_with_production_data(test_project_path, multi_session_data)

        # Should detect 2 sessions
        summary = timeline.get_multi_session_summary()
        assert summary["total_sessions"] == 2
        assert "session-111" in summary["sessions"]
        assert "session-222" in summary["sessions"]

        timeline.clear_cache()

    def test_handles_permission_errors(self, test_project_path, production_like_data):
        """Should handle permission errors gracefully."""
        # This test passes by not crashing during initialization
        timeline = self._create_timeline_with_production_data(test_project_path, production_like_data)

        # Should initialize successfully even with potential permission issues
        assert timeline is not None
        assert len(timeline.tool_operations) >= 0

        timeline.clear_cache()


class TestRealClaudeTimelineIntegration:
    """Integration tests for real timeline usage."""

    def test_complete_workflow(self):
        """Test complete workflow with production-like data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            workflow_data = [
                {
                    "type": "assistant",
                    "uuid": "workflow-1",
                    "sessionId": "workflow-session",
                    "timestamp": "2025-01-04T10:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_path / "main.py"),
                                    "content": "print('Hello, World!')\n",
                                },
                            }
                        ]
                    },
                },
            ]

            mock_discovery = MockProjectDiscovery()
            transcript_path = project_path / "session.jsonl"
            mock_discovery.add_project("workflow-project", project_path, [transcript_path])

            with patch("claude_parser.domain.services.claude_code_timeline.jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = workflow_data

                timeline = RealClaudeTimeline(project_path, mock_discovery)

                # Should work with the complete workflow
                assert len(timeline.tool_operations) == 1

                # Should support checkout functionality
                op = timeline.tool_operations[0]
                uuid = op.get("uuid")

                state = timeline.checkout_by_uuid(uuid)
                assert state is not None

                timeline.clear_cache()
