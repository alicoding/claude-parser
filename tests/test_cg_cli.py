"""
Comprehensive tests for cg (claude-git) CLI command.
Tests all git-like functionality without requiring real Claude Code data.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from unittest.mock import Mock, patch

from claude_parser.cg_cli import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_timeline():
    """Create mock ClaudeCodeTimeline with realistic data."""
    timeline = Mock()

    # Mock tool operations
    timeline.tool_operations = [
        {
            "uuid": "abc12345-1234-1234-1234-123456789abc",
            "sessionId": "session123",
            "timestamp": "2025-01-04T10:15:30Z",
            "tool_name": "Read",
            "file_path": "app.py",
            "tool_input": {"file_path": "app.py"},
        },
        {
            "uuid": "def67890-1234-1234-1234-123456789def",
            "sessionId": "session123",
            "timestamp": "2025-01-04T10:16:45Z",
            "tool_name": "Edit",
            "file_path": "app.py",
            "tool_input": {
                "file_path": "app.py",
                "old_string": 'print("hello")',
                "new_string": 'print("world")',
            },
        },
    ]

    # Mock multi-session summary
    timeline.get_multi_session_summary.return_value = {
        "total_sessions": 1,
        "total_operations": 2,
        "sessions": {
            "session123": {
                "operations": 2,
                "files_modified": ["app.py"],
                "first_timestamp": "2025-01-04T10:15:30Z",
                "last_timestamp": "2025-01-04T10:16:45Z",
            }
        },
    }

    # Mock checkout
    timeline.checkout_by_uuid.return_value = {
        "app.py": {"content": 'print("world")', "timestamp": "2025-01-04T10:16:45Z"}
    }

    # Mock diff
    timeline.get_operation_diff.return_value = {
        "operation": "Edit",
        "file_path": "app.py",
        "diff": [
            "--- a/app.py",
            "+++ b/app.py",
            "@@ -1 +1 @@",
            '-print("hello")',
            '+print("world")',
        ],
    }

    timeline.clear_cache = Mock()

    return timeline


class TestCgStatus:
    """Test cg status command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_status_basic(self, mock_timeline_class, runner, mock_timeline):
        """Test basic status command."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
        assert "📊 Timeline Summary" in result.stdout
        assert "2 operations from 1 sessions" in result.stdout
        assert "📂 Project:" in result.stdout
        assert "app.py: 2 operations" in result.stdout

        mock_timeline.clear_cache.assert_called_once()

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_status_with_sessions(self, mock_timeline_class, runner, mock_timeline):
        """Test status command with --sessions flag."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["status", "--sessions"])

        assert result.exit_code == 0
        assert "📊 Multi-Session Summary" in result.stdout
        assert "Sessions: 1" in result.stdout
        assert "Operations: 2" in result.stdout
        assert "📋 Session session1" in result.stdout  # Truncated session ID

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_status_no_transcripts(self, mock_timeline_class, runner):
        """Test status when no transcripts found."""
        mock_timeline_class.side_effect = ValueError("No Claude Code transcripts found")

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 1
        assert "❌ No Claude Code transcripts found" in result.stdout
        assert (
            "💡 Make sure you're in a directory that Claude Code has worked on"
            in result.stdout
        )


class TestCgLog:
    """Test cg log command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_log_basic(self, mock_timeline_class, runner, mock_timeline):
        """Test basic log command."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["log"])

        assert result.exit_code == 0
        assert "📊 Timeline Summary" in result.stdout
        assert "2 operations from 1 sessions" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_log_with_file_filter(self, mock_timeline_class, runner, mock_timeline):
        """Test log command with --file filter."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["log", "--file", "app.py"])

        assert result.exit_code == 0
        assert "📅 Timeline for app.py" in result.stdout
        assert "abc12345 (Read)" in result.stdout
        assert "def67890 (Edit)" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_log_with_sessions(self, mock_timeline_class, runner, mock_timeline):
        """Test log command with --sessions flag."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["log", "--sessions"])

        assert result.exit_code == 0
        assert "📋 Recent Operations:" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_log_with_limit(self, mock_timeline_class, runner, mock_timeline):
        """Test log command with --limit flag."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["log", "--limit", "1"])

        assert result.exit_code == 0
        # Should still show summary even with limit


class TestCgCheckout:
    """Test cg checkout command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_checkout_success(self, mock_timeline_class, runner, mock_timeline):
        """Test successful checkout to UUID."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["checkout", "def67890"])

        assert result.exit_code == 0
        assert "✅ Restored to UUID def67890" in result.stdout
        assert "📄 app.py" in result.stdout

        # The CLI expands partial UUIDs to full UUIDs
        mock_timeline.checkout_by_uuid.assert_called_with(
            "def67890-1234-1234-1234-123456789def"
        )

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_checkout_not_found(self, mock_timeline_class, runner, mock_timeline):
        """Test checkout when UUID not found."""
        mock_timeline_class.return_value = mock_timeline
        mock_timeline.checkout_by_uuid.return_value = None

        result = runner.invoke(app, ["checkout", "nonexistent"])

        assert (
            result.exit_code == 0
        )  # Command doesn't exit with error, just shows message
        assert "❌ Cannot restore to UUID nonexistent" in result.stdout
        assert "💡 Use 'cg log' to see available UUIDs" in result.stdout


class TestCgUndo:
    """Test cg undo command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_undo_steps(self, mock_timeline_class, runner, mock_timeline):
        """Test undo N steps."""
        mock_timeline_class.return_value = mock_timeline

        # Mock successful undo
        mock_timeline.checkout_by_uuid.return_value = {
            "app.py": {
                "content": "original content",
                "timestamp": "2025-01-04T10:15:30Z",
            }
        }

        result = runner.invoke(app, ["undo", "1"])

        assert result.exit_code == 0
        assert "✅ Undid 1 change(s)" in result.stdout
        assert "📄 Restored:" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_undo_too_many_steps(self, mock_timeline_class, runner, mock_timeline):
        """Test undo when requesting too many steps."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["undo", "10"])

        assert result.exit_code == 0
        assert "❌ Cannot undo 10 steps. Only 1 operations available." in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_undo_zero_steps(self, mock_timeline_class, runner, mock_timeline):
        """Test undo with zero steps."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["undo", "0"])

        assert result.exit_code == 0
        assert "❌ Steps must be positive number" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_undo_to_uuid(self, mock_timeline_class, runner, mock_timeline):
        """Test undo --to with specific UUID."""
        mock_timeline_class.return_value = mock_timeline

        # Mock successful checkout
        mock_timeline.checkout_by_uuid.return_value = {
            "app.py": {"content": "print('hello')", "timestamp": "2023-01-01T00:00:00Z"}
        }

        result = runner.invoke(app, ["undo", "--to", "abc12345"])

        assert result.exit_code == 0
        assert "✅ Restored to UUID abc12345" in result.stdout
        assert "📄 app.py" in result.stdout
        mock_timeline.checkout_by_uuid.assert_called_once_with("abc12345")

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_undo_to_uuid_not_found(self, mock_timeline_class, runner, mock_timeline):
        """Test undo --to with non-existent UUID."""
        mock_timeline_class.return_value = mock_timeline

        # Mock failed checkout
        mock_timeline.checkout_by_uuid.return_value = None

        result = runner.invoke(app, ["undo", "--to", "invalid"])

        assert result.exit_code == 0
        assert "❌ Cannot restore to UUID invalid" in result.stdout
        mock_timeline.checkout_by_uuid.assert_called_once_with("invalid")


class TestCgShow:
    """Test cg show command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_show_operation(self, mock_timeline_class, runner, mock_timeline):
        """Test show command with valid UUID."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["show", "def67890"])

        assert result.exit_code == 0
        assert "🔍 Operation def67890" in result.stdout
        assert "Type: Edit" in result.stdout
        assert "File: app.py" in result.stdout
        assert "Session: session1" in result.stdout  # Truncated
        assert "Timestamp: 2025-01-04T10:16:45" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_show_operation_not_found(self, mock_timeline_class, runner, mock_timeline):
        """Test show command with invalid UUID."""
        mock_timeline_class.return_value = mock_timeline

        # Mock empty tool_operations for this test
        mock_timeline.tool_operations = []

        result = runner.invoke(app, ["show", "nonexistent"])

        assert result.exit_code == 0
        assert "❌ Operation nonexistent not found" in result.stdout
        assert "💡 Use 'cg log' to see available operations" in result.stdout


class TestCgDiff:
    """Test cg diff command."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_diff_basic(self, mock_timeline_class, runner, mock_timeline):
        """Test basic diff command (recent changes)."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["diff"])

        assert result.exit_code == 0
        assert "🔍 Recent changes (Edit on app.py)" in result.stdout
        assert "--- a/app.py" in result.stdout
        assert "+++ b/app.py" in result.stdout
        assert '-print("hello")' in result.stdout
        assert '+print("world")' in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_diff_with_uuid(self, mock_timeline_class, runner, mock_timeline):
        """Test diff command with specific UUID."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["diff", "--uuid", "def67890"])

        assert result.exit_code == 0
        assert "🔍 Changes at def67890 (Edit on app.py)" in result.stdout
        assert "--- a/app.py" in result.stdout
        assert "+++ b/app.py" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_diff_uuid_not_found(self, mock_timeline_class, runner, mock_timeline):
        """Test diff with UUID that doesn't exist."""
        mock_timeline_class.return_value = mock_timeline
        mock_timeline.get_operation_diff.return_value = None

        result = runner.invoke(app, ["diff", "--uuid", "nonexistent"])

        assert result.exit_code == 0
        assert "❌ No operation found for UUID nonexist" in result.stdout

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_diff_no_recent_changes(self, mock_timeline_class, runner, mock_timeline):
        """Test diff when no recent changes exist."""
        mock_timeline_class.return_value = mock_timeline
        mock_timeline.tool_operations = []  # No operations

        result = runner.invoke(app, ["diff"])

        assert result.exit_code == 0
        assert "📭 No operations found" in result.stdout


class TestCgCommandIntegration:
    """Test command integration and edge cases."""

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_project_path_argument(self, mock_timeline_class, runner, mock_timeline):
        """Test commands with explicit project path."""
        mock_timeline_class.return_value = mock_timeline

        result = runner.invoke(app, ["status", "/specific/path"])

        assert result.exit_code == 0
        mock_timeline_class.assert_called_with(Path("/specific/path"))

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_timeline_cleanup(self, mock_timeline_class, runner, mock_timeline):
        """Test that timeline cleanup is always called."""
        mock_timeline_class.return_value = mock_timeline

        runner.invoke(app, ["status"])

        mock_timeline.clear_cache.assert_called_once()

    @patch("claude_parser.cg_cli.ClaudeCodeTimeline")
    def test_timeline_exception_handling(
        self, mock_timeline_class, runner, mock_timeline
    ):
        """Test proper cleanup even when timeline operations fail."""
        mock_timeline_class.return_value = mock_timeline
        mock_timeline.get_multi_session_summary.side_effect = Exception("Test error")

        # Should handle exception and still clean up
        result = runner.invoke(app, ["status", "--sessions"])

        mock_timeline.clear_cache.assert_called_once()


class TestCgHelp:
    """Test help and usage information."""

    def test_main_help(self, runner):
        """Test main help command."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Git-like interface for Claude Code operations" in result.stdout
        assert "status" in result.stdout
        assert "log" in result.stdout
        assert "checkout" in result.stdout
        assert "undo" in result.stdout
        assert "show" in result.stdout
        assert "diff" in result.stdout

    def test_status_help(self, runner):
        """Test status command help."""
        result = runner.invoke(app, ["status", "--help"])

        assert result.exit_code == 0
        assert "Show current project state and session information" in result.stdout
        assert "--sessions" in result.stdout

    def test_log_help(self, runner):
        """Test log command help."""
        result = runner.invoke(app, ["log", "--help"])

        assert result.exit_code == 0
        assert "View operation history across all Claude Code sessions" in result.stdout
        assert "--file" in result.stdout
        assert "--limit" in result.stdout
        assert "--sessions" in result.stdout
