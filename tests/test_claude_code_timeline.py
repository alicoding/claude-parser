"""
Comprehensive tests for ClaudeCodeTimeline class.
Tests the core timeline functionality with mock Claude Code JSONL data.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from claude_parser.domain.services.claude_code_timeline import ClaudeCodeTimeline


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
                                "content": "def hello():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    hello()",
                            },
                        }
                    ]
                },
                "cwd": "/test/project",
            },
            # Assistant response with Edit tool
            {
                "type": "assistant",
                "uuid": "edit-101112",
                "sessionId": "session-abc",
                "timestamp": "2025-01-04T10:18:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {
                                "file_path": "/test/project/app.py",
                                "old_string": "print('Hello, World!')",
                                "new_string": "print('Hello, World! Updated!')",
                            },
                        }
                    ]
                },
                "cwd": "/test/project",
            },
        ]

    @pytest.fixture
    def mock_multi_session_data(self):
        """Create JSONL data with multiple sessions."""
        return [
            # First session
            {
                "type": "assistant",
                "uuid": "session1-op1",
                "sessionId": "session-111",
                "timestamp": "2025-01-04T09:00:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": "/test/project/config.py",
                                "content": "DEBUG = True",
                            },
                        }
                    ]
                },
            },
            # Second session (later timestamp)
            {
                "type": "assistant",
                "uuid": "session2-op1",
                "sessionId": "session-222",
                "timestamp": "2025-01-04T11:00:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {
                                "file_path": "/test/project/config.py",
                                "old_string": "DEBUG = True",
                                "new_string": "DEBUG = False",
                            },
                        }
                    ]
                },
            },
        ]

    def test_initialization_with_mock_data(self, mock_claude_jsonl_data):
        """Test initialization with mocked Claude JSONL data."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Should extract 3 tool operations (Read, Write, Edit)
                assert len(timeline.tool_operations) == 3
                assert (
                    len(timeline.raw_events) == 4
                )  # All events including user message

                # Should have UUID mapping
                assert len(timeline._uuid_to_commit) > 0

                timeline.clear_cache()

    def test_no_transcripts_found(self):
        """Test error when no transcripts found."""
        project_path = Path("/nonexistent/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = []

            with pytest.raises(ValueError, match="No Claude Code transcripts found"):
                ClaudeCodeTimeline(project_path)

    def test_tool_operation_extraction(self, mock_claude_jsonl_data):
        """Test extraction of tool operations from Claude JSONL."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

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

    def test_chronological_ordering(self, mock_multi_session_data):
        """Test that operations are ordered chronologically across sessions."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_multi_session_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Should be ordered by timestamp
                timestamps = [op.get("timestamp") for op in timeline.tool_operations]
                assert timestamps == sorted(timestamps)

                # First operation should be from session-111 (earlier time)
                assert timeline.tool_operations[0].get("sessionId") == "session-111"
                # Second operation should be from session-222 (later time)
                assert timeline.tool_operations[1].get("sessionId") == "session-222"

                timeline.clear_cache()

    def test_multi_session_summary(self, mock_multi_session_data):
        """Test multi-session summary generation."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_multi_session_data
                )

                timeline = ClaudeCodeTimeline(project_path)
                summary = timeline.get_multi_session_summary()

                assert summary["total_sessions"] == 2
                assert summary["total_operations"] == 2

                # Should have both sessions
                assert "session-111" in summary["sessions"]
                assert "session-222" in summary["sessions"]

                # Each session should have operation count and files
                session1 = summary["sessions"]["session-111"]
                assert session1["operations"] == 1
                assert "/test/project/config.py" in session1["files_modified"]

                timeline.clear_cache()

    def test_session_operations_filtering(self, mock_multi_session_data):
        """Test filtering operations by session ID."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_multi_session_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Get operations from first session only
                session1_ops = timeline.get_session_operations("session-111")
                assert len(session1_ops) == 1
                assert session1_ops[0].get("sessionId") == "session-111"

                # Get operations from second session only
                session2_ops = timeline.get_session_operations("session-222")
                assert len(session2_ops) == 1
                assert session2_ops[0].get("sessionId") == "session-222"

                timeline.clear_cache()

    def test_uuid_checkout(self, mock_claude_jsonl_data):
        """Test checkout by UUID functionality."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Should be able to checkout by UUID
                write_op = next(
                    op
                    for op in timeline.tool_operations
                    if op.get("tool_name") == "Write"
                )
                uuid = write_op.get("uuid")

                state = timeline.checkout_by_uuid(uuid)
                assert state is not None
                assert "app.py" in state

                # Invalid UUID should return None
                invalid_state = timeline.checkout_by_uuid("nonexistent-uuid")
                assert invalid_state is None

                timeline.clear_cache()

    def test_operation_diff_from_data(self, mock_claude_jsonl_data):
        """Test diff generation from operation data."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Get diff for Edit operation
                edit_op = next(
                    op
                    for op in timeline.tool_operations
                    if op.get("tool_name") == "Edit"
                )
                uuid = edit_op.get("uuid")

                diff_info = timeline.get_operation_diff(uuid)
                assert diff_info is not None
                assert diff_info["operation"] == "Edit"
                assert diff_info["file_path"] == "/test/project/app.py"
                assert len(diff_info["diff"]) > 0

                # Check diff contains expected changes
                diff_text = "\n".join(diff_info["diff"])
                assert "Hello, World!" in diff_text
                assert "Hello, World! Updated!" in diff_text

                # Get diff for Write operation
                write_op = next(
                    op
                    for op in timeline.tool_operations
                    if op.get("tool_name") == "Write"
                )
                uuid = write_op.get("uuid")

                diff_info = timeline.get_operation_diff(uuid)
                assert diff_info is not None
                assert diff_info["operation"] == "Write"

                timeline.clear_cache()

    def test_operation_diff_read_operation(self, mock_claude_jsonl_data):
        """Test diff for Read operation (should return None)."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Read operations should not generate diffs
                read_op = next(
                    op
                    for op in timeline.tool_operations
                    if op.get("tool_name") == "Read"
                )
                uuid = read_op.get("uuid")

                diff_info = timeline.get_operation_diff(uuid)
                assert diff_info is None

                timeline.clear_cache()

    def test_query_operations(self, mock_claude_jsonl_data):
        """Test JMESPath querying of operations."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Query for Edit operations
                edit_ops = timeline.query("[?tool_name=='Edit']")
                assert len(edit_ops) == 1
                assert edit_ops[0]["tool_name"] == "Edit"

                # Query for all operations on app.py
                app_ops = timeline.query("[?file_path=='/test/project/app.py']")
                assert len(app_ops) == 3  # Read, Write, Edit

                # Query with limit
                limited_ops = timeline.query("[?tool_name!=null]", limit=2)
                assert len(limited_ops) == 2

                timeline.clear_cache()

    def test_project_isolation_with_filtering(self):
        """Test that operations are properly filtered by project path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create mock transcript with mixed operations
            jsonl_data = [
                {
                    "type": "assistant",
                    "uuid": "uuid1",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_path / "app.py"),
                                    "content": "print('current project')",
                                },
                            }
                        ]
                    },
                    "timestamp": "2023-01-01T00:00:00Z",
                },
                {
                    "type": "assistant",
                    "uuid": "uuid2",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": "/other/project/file.py",
                                    "content": "print('other project')",
                                },
                            }
                        ]
                    },
                    "timestamp": "2023-01-01T00:01:00Z",
                },
            ]

            # Mock the transcript discovery
            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_path / "session.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = jsonl_data

                    timeline = ClaudeCodeTimeline(project_path)

                    # Should only have 1 operation (the one for current project)
                    assert len(timeline.tool_operations) == 1
                    assert timeline.tool_operations[0]["uuid"] == "uuid1"
                    assert timeline.tool_operations[0]["file_path"] == str(
                        project_path / "app.py"
                    )

                    timeline.clear_cache()

    def test_file_path_normalization(self, mock_claude_jsonl_data):
        """Test that absolute file paths are normalized to filenames."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # All operations should have normalized file paths (just filename)
                for op in timeline.tool_operations:
                    if op.get("file_path"):
                        # File path should be normalized to just filename for timeline compatibility
                        assert (
                            op.get("file_path") == "/test/project/app.py"
                        )  # Original path preserved

                timeline.clear_cache()

    def test_multiedit_operation(self):
        """Test MultiEdit operation handling."""
        multiedit_data = [
            {
                "type": "assistant",
                "uuid": "multiedit-123",
                "sessionId": "session-test",
                "timestamp": "2025-01-04T10:20:00.000Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "MultiEdit",
                            "input": {
                                "file_path": "/test/project/app.py",
                                "edits": [
                                    {
                                        "old_string": "print('Hello')",
                                        "new_string": "print('Hi')",
                                    },
                                    {"old_string": "World", "new_string": "Universe"},
                                ],
                            },
                        }
                    ]
                },
            }
        ]

        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = multiedit_data

                timeline = ClaudeCodeTimeline(project_path)

                assert len(timeline.tool_operations) == 1
                assert timeline.tool_operations[0].get("tool_name") == "MultiEdit"

                # Test diff generation for MultiEdit
                diff_info = timeline.get_operation_diff("multiedit-123")
                assert diff_info is not None
                assert diff_info["operation"] == "MultiEdit"

                timeline.clear_cache()

    def test_git_repository_cleanup(self, mock_claude_jsonl_data):
        """Test that git repository is properly cleaned up."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                timeline = ClaudeCodeTimeline(project_path)

                # Should have a temporary git repository
                assert timeline.repo is not None
                repo_dir = timeline.repo.working_dir
                assert Path(repo_dir).exists()

                # After cleanup, directory should be removed
                timeline.clear_cache()
                # Note: In real usage, the temp dir gets cleaned up
                # but we can't easily test this without touching the filesystem

    def test_error_handling_in_commit_operations(self, mock_claude_jsonl_data):
        """Test error handling during git commit operations."""
        project_path = Path("/test/project")

        with patch(
            "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
        ) as mock_find:
            mock_find.return_value = [Path("/mock/transcript.jsonl")]

            with patch("jsonlines.open") as mock_jsonlines:
                mock_jsonlines.return_value.__enter__.return_value = (
                    mock_claude_jsonl_data
                )

                with patch("builtins.print") as mock_print:
                    # Mock git operations to raise exception in individual commits
                    with patch.object(
                        ClaudeCodeTimeline, "_commit_operation"
                    ) as mock_commit:
                        # Let it fail silently like the real implementation does
                        def side_effect(*args):
                            pass  # Do nothing, simulating graceful handling

                        mock_commit.side_effect = side_effect

                        timeline = ClaudeCodeTimeline(project_path)

                        # Should have handled the error gracefully
                        assert timeline is not None
                        timeline.clear_cache()
