"""
Integration tests for CG CLI workflow.

Tests the complete workflow with real-like data to ensure
everything works together properly.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from claude_parser.cg_cli import app


class TestCgIntegrationWorkflow:
    """Test complete CG workflow with realistic data."""

    @pytest.fixture
    def runner(self):
        """CLI test runner."""
        return CliRunner()

    def realistic_transcript_data_factory(self, project_path):
        """Create realistic transcript data for testing."""
        return [
            # Initial Write operation
            {
                "type": "assistant",
                "uuid": "write-001-uuid-full",
                "sessionId": "session-1",
                "timestamp": "2025-01-04T10:00:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": str(project_path / "app.py"),
                                "content": "def hello():\n    print('hello')\n",
                            },
                        }
                    ]
                },
            },
            # Edit operation
            {
                "type": "assistant",
                "uuid": "edit-001-uuid-full",
                "sessionId": "session-1",
                "timestamp": "2025-01-04T10:01:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Edit",
                            "input": {
                                "file_path": str(project_path / "app.py"),
                                "old_string": "def hello():\n    print('hello')",
                                "new_string": "def hello():\n    print('hello world')",
                            },
                        }
                    ]
                },
            },
            # MultiEdit operation
            {
                "type": "assistant",
                "uuid": "multi-001-uuid-full",
                "sessionId": "session-1",
                "timestamp": "2025-01-04T10:02:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "MultiEdit",
                            "input": {
                                "file_path": str(project_path / "app.py"),
                                "edits": [
                                    {
                                        "old_string": "print('hello world')",
                                        "new_string": "print('Hello, World!')",
                                    }
                                ],
                            },
                        }
                    ]
                },
            },
            # Second session with new file
            {
                "type": "assistant",
                "uuid": "write-002-uuid-full",
                "sessionId": "session-2",
                "timestamp": "2025-01-04T11:00:00Z",
                "message": {
                    "content": [
                        {
                            "type": "tool_use",
                            "name": "Write",
                            "input": {
                                "file_path": str(project_path / "utils.py"),
                                "content": "def utility_function():\n    return 'utils'\n",
                            },
                        }
                    ]
                },
            },
        ]

    def test_complete_cg_workflow(self, runner):
        """Test complete CG workflow from status to undo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            # Create realistic data with actual project path
            realistic_transcript_data = self.realistic_transcript_data_factory(
                project_path
            )

            # Mock transcript discovery
            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_path / "session.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = (
                        realistic_transcript_data
                    )

                    # Test 1: Status command
                    result = runner.invoke(app, ["status", str(project_path)])
                    assert result.exit_code == 0
                    assert "📊 Timeline Summary" in result.stdout

                    # Test 2: Log command
                    result = runner.invoke(app, ["log", str(project_path)])
                    assert result.exit_code == 0
                    assert "4 operations" in result.stdout
                    assert "app.py: 3 operations" in result.stdout
                    assert "utils.py: 1 operations" in result.stdout

                    # Test 3: Show command with partial UUID
                    result = runner.invoke(app, ["show", "edit-001", str(project_path)])
                    assert result.exit_code == 0
                    assert "🔍 Operation edit-001" in result.stdout

                    # Test 4: Diff command
                    result = runner.invoke(
                        app, ["diff", "--uuid", "edit-001", str(project_path)]
                    )
                    assert result.exit_code == 0
                    assert "🔍 Changes at edit-001" in result.stdout

                    # Test 5: Checkout command
                    result = runner.invoke(
                        app, ["checkout", "write-001", str(project_path)]
                    )
                    assert result.exit_code == 0
                    assert "✅ Checked out to write-001" in result.stdout

                    # Test 6: Undo command with steps
                    result = runner.invoke(app, ["undo", "1", str(project_path)])
                    assert result.exit_code == 0
                    assert "✅ Undid 1 change(s)" in result.stdout

                    # Test 7: Undo to specific UUID
                    result = runner.invoke(
                        app, ["undo", str(project_path), "--to", "write-001"]
                    )
                    assert result.exit_code == 0
                    assert "✅ Restored to UUID write-001" in result.stdout

    def test_project_isolation_integration(self, runner):
        """Test that project isolation works end-to-end."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_a = Path(temp_dir) / "project_a"
            project_b = Path(temp_dir) / "project_b"
            project_a.mkdir()
            project_b.mkdir()

            # Data for project A
            project_a_data = [
                {
                    "type": "assistant",
                    "uuid": "project-a-op1",
                    "sessionId": "session-a",
                    "timestamp": "2025-01-04T10:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_a / "app_a.py"),
                                    "content": "# Project A file\n",
                                },
                            }
                        ]
                    },
                }
            ]

            # Data for project B
            project_b_data = [
                {
                    "type": "assistant",
                    "uuid": "project-b-op1",
                    "sessionId": "session-b",
                    "timestamp": "2025-01-04T10:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_b / "app_b.py"),
                                    "content": "# Project B file\n",
                                },
                            }
                        ]
                    },
                }
            ]

            # Test project A isolation
            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_a / "session_a.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = project_a_data

                    result = runner.invoke(app, ["log", str(project_a)])
                    assert result.exit_code == 0
                    # Check for operation presence (using partial UUID)
                    assert "project-a" in result.stdout
                    assert "project-b-op1" not in result.stdout  # Should be isolated
                    assert "app_a.py" in result.stdout
                    assert "app_b.py" not in result.stdout  # Should be isolated

            # Test project B isolation
            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_b / "session_b.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = project_b_data

                    result = runner.invoke(app, ["log", str(project_b)])
                    assert result.exit_code == 0
                    # Check for operation presence (using partial UUID)
                    assert "project-b" in result.stdout
                    assert "project-a-op1" not in result.stdout  # Should be isolated
                    assert "app_b.py" in result.stdout
                    assert "app_a.py" not in result.stdout  # Should be isolated

    def test_multi_session_support(self, runner):
        """Test multi-session functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            multi_session_data = [
                # Session 1 operations
                {
                    "type": "assistant",
                    "uuid": "s1-op1-uuid",
                    "sessionId": "session-1",
                    "timestamp": "2025-01-04T10:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_path / "file1.py"),
                                    "content": "# Session 1 file\n",
                                },
                            }
                        ]
                    },
                },
                # Session 2 operations
                {
                    "type": "assistant",
                    "uuid": "s2-op1-uuid",
                    "sessionId": "session-2",
                    "timestamp": "2025-01-04T11:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_path / "file2.py"),
                                    "content": "# Session 2 file\n",
                                },
                            }
                        ]
                    },
                },
            ]

            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_path / "multi_session.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = (
                        multi_session_data
                    )

                    # Test sessions view
                    result = runner.invoke(
                        app, ["status", "--sessions", str(project_path)]
                    )
                    assert result.exit_code == 0
                    assert "Multi-Session Summary" in result.stdout
                    assert "Sessions: 2" in result.stdout

                    # Test log with sessions
                    result = runner.invoke(
                        app, ["log", "--sessions", str(project_path)]
                    )
                    assert result.exit_code == 0
                    # Check for operations from both sessions
                    assert "s1-op1-u" in result.stdout or "session-1" in result.stdout
                    assert "s2-op1-u" in result.stdout or "session-2" in result.stdout

    def test_error_handling_integration(self, runner):
        """Test error handling in integration scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "nonexistent"

            # Test with no transcripts found
            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = []

                result = runner.invoke(app, ["status", str(project_path)])
                assert result.exit_code == 1
                assert "No Claude Code transcripts found" in result.stdout

                result = runner.invoke(app, ["log", str(project_path)])
                assert result.exit_code == 1

    def test_uuid_expansion_integration(self, runner):
        """Test UUID expansion across multiple commands."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "project"
            project_path.mkdir()

            test_data = [
                {
                    "type": "assistant",
                    "uuid": "abcd1234-5678-9012-3456-789012345678",
                    "sessionId": "session-1",
                    "timestamp": "2025-01-04T10:00:00Z",
                    "message": {
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Write",
                                "input": {
                                    "file_path": str(project_path / "test.py"),
                                    "content": "print('test')\n",
                                },
                            }
                        ]
                    },
                }
            ]

            with patch(
                "claude_parser.domain.services.claude_code_timeline.find_all_transcripts_for_cwd"
            ) as mock_find:
                mock_find.return_value = [str(project_path / "session.jsonl")]

                with patch("jsonlines.open") as mock_jsonlines:
                    mock_jsonlines.return_value.__enter__.return_value = test_data

                    # Test partial UUID works in show
                    result = runner.invoke(app, ["show", "abcd1234", str(project_path)])
                    assert result.exit_code == 0
                    assert "🔍 Operation abcd1234" in result.stdout

                    # Test partial UUID works in checkout
                    result = runner.invoke(
                        app, ["checkout", "abcd1234", str(project_path)]
                    )
                    assert result.exit_code == 0
                    assert "✅ Restored to UUID abcd1234" in result.stdout

                    # Test partial UUID works in undo --to
                    result = runner.invoke(
                        app, ["undo", str(project_path), "--to", "abcd1234"]
                    )
                    assert result.exit_code == 0
                    assert "✅ Restored to UUID abcd1234" in result.stdout
