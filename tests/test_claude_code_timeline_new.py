"""
Comprehensive tests for ClaudeCodeTimeline class.
Tests the core timeline functionality with mock Claude Code JSONL data.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from claude_parser.domain.services.claude_code_timeline import ClaudeCodeTimeline
from claude_parser.infrastructure.discovery import MockProjectDiscovery


class TestClaudeCodeTimeline:
    """Test ClaudeCodeTimeline core functionality."""

    @pytest.fixture
    def mock_claude_jsonl_data(self):
        """Create realistic Claude Code JSONL data for testing."""
        return [
            # User message
            {
                "type": "user",
                "uuid": "user-123",
                "sessionId": "session-abc",
                "timestamp": "2025-01-04T10:15:30.000Z",
                "message": {"content": "Create a hello world function"},
                "cwd": "/test/project",
            },
            # Assistant response with Read tool
            {
                "type": "assistant",
                "uuid": "read-456",
                "sessionId": "session-abc",
                "timestamp": "2025-01-04T10:16:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Read",
                            "input": {"file_path": "/test/project/app.py"},
                        }
                    ]
                },
                "cwd": "/test/project",
            },
            # Assistant response with Write tool
            {
                "type": "assistant",
                "uuid": "write-789",
                "sessionId": "session-abc",
                "timestamp": "2025-01-04T10:17:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": "/test/project/app.py",
                                "content": "def hello():\n    print('Hello, World!')\n",
                            },
                        }
                    ]
                },
                "cwd": "/test/project",
            },
            # Assistant response with Edit tool
            {
                "type": "assistant",
                "uuid": "edit-012",
                "sessionId": "session-abc",
                "timestamp": "2025-01-04T10:18:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {
                                "file_path": "/test/project/app.py",
                                "old_string": "Hello, World!",
                                "new_string": "Hello, World! Updated!",
                            },
                        }
                    ]
                },
                "cwd": "/test/project",
            },
        ]

    def _create_timeline_with_mock_data(self, project_path, jsonl_data):
        """Helper method to create ClaudeCodeTimeline with mock data."""
        mock_discovery = MockProjectDiscovery()
        transcript_path = project_path / "session.jsonl"
        mock_discovery.add_project("test-project", project_path, [transcript_path])

        with patch("claude_parser.domain.services.claude_code_timeline.jsonlines.open") as mock_jsonlines:
            mock_jsonlines.return_value.__enter__.return_value = jsonl_data
            return ClaudeCodeTimeline(project_path, mock_discovery)

    def test_initialization_with_mock_data(self, mock_claude_jsonl_data):
        """Test initialization with mocked Claude JSONL data."""
        project_path = Path("/test/project")

        timeline = self._create_timeline_with_mock_data(project_path, mock_claude_jsonl_data)

        # Should extract 3 tool operations (Read, Write, Edit)
        assert len(timeline.tool_operations) == 3
        assert len(timeline.raw_events) == 4  # All events including user message

        # Should have UUID mapping
        assert len(timeline._uuid_to_commit) > 0

        timeline.clear_cache()

    def test_no_transcripts_found(self):
        """Test error when no transcripts found."""
        project_path = Path("/nonexistent/project")

        # Create empty mock discovery service (no projects added)
        mock_discovery = MockProjectDiscovery()

        with pytest.raises(ValueError, match="No Claude Code transcripts found"):
            ClaudeCodeTimeline(project_path, mock_discovery)

    def test_tool_operation_extraction(self, mock_claude_jsonl_data):
        """Test extraction of tool operations from Claude JSONL."""
        project_path = Path("/test/project")

        timeline = self._create_timeline_with_mock_data(project_path, mock_claude_jsonl_data)

        # Should have extracted Read, Write, Edit operations
        tool_names = [op.get("tool_name") for op in timeline.tool_operations]
        assert "Read" in tool_names
        assert "Write" in tool_names
        assert "Edit" in tool_names

        # Each operation should have required fields
        for op in timeline.tool_operations:
            assert "uuid" in op
            assert "sessionId" in op
            assert "timestamp" in op
            assert "tool_name" in op
            assert "tool_input" in op
            assert "file_path" in op

        timeline.clear_cache()
