"""
Integration tests for CG CLI commands with mock data.
Tests complete workflows from status to undo.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from claude_parser.cg_cli import app
from claude_parser.infrastructure.discovery import MockProjectDiscovery


class TestCgIntegrationWorkflow:
    """Test complete CG workflow integration."""

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

            # Create mock discovery service
            mock_discovery = MockProjectDiscovery()
            transcript_path = project_path / "session.jsonl"
            mock_discovery.add_project("test-project", project_path, [transcript_path])

            # Mock the discovery service creation and jsonlines
            with patch("claude_parser.cg_cli.ConfigurableProjectDiscovery") as mock_discovery_class:
                mock_discovery_class.return_value = mock_discovery

                with patch("claude_parser.domain.services.claude_code_timeline.jsonlines.open") as mock_jsonlines:
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

    def test_error_handling_integration(self, runner):
        """Test error handling in CLI integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "nonexistent"

            # Create empty mock discovery (no projects)
            mock_discovery = MockProjectDiscovery()

            with patch("claude_parser.cg_cli.ConfigurableProjectDiscovery") as mock_discovery_class:
                mock_discovery_class.return_value = mock_discovery

                # Should handle missing project gracefully
                result = runner.invoke(app, ["status", str(project_path)])
                assert result.exit_code == 1  # Should exit with error
                assert "❌" in result.stdout
