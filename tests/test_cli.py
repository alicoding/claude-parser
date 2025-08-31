"""TDD tests for claude-parser CLI - Write tests FIRST!"""

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_jsonl(tmp_path):
    """Create sample JSONL file for testing."""
    file = tmp_path / "test.jsonl"
    data = {
        "type": "user",
        "uuid": "test-001",
        "sessionId": "test-session",
        "timestamp": "2025-08-29T00:00:00Z",
        "message": {"role": "user", "content": "Test message"}
    }
    file.write_text(json.dumps(data) + "\n")
    return str(file)


def test_cli_import():
    """Test that CLI module can be imported."""
    from claude_parser.cli import app
    assert app is not None


def test_parse_command(runner, sample_jsonl):
    """Test basic parse command."""
    from claude_parser.cli import app
    
    result = runner.invoke(app, ["parse", sample_jsonl])
    assert result.exit_code == 0
    assert "Messages:" in result.output


def test_parse_with_stats(runner, sample_jsonl):
    """Test parse with --stats flag."""
    from claude_parser.cli import app
    
    result = runner.invoke(app, ["parse", sample_jsonl, "--stats"])
    assert result.exit_code == 0
    # Should show statistics
    assert any(word in result.output.lower() for word in ["token", "statistic", "total"])


def test_find_command(runner, monkeypatch):
    """Test find current transcript."""
    from claude_parser.cli import app
    
    # Mock the find function
    monkeypatch.setattr(
        "claude_parser.find_current_transcript",
        lambda: "/path/to/transcript.jsonl"
    )
    
    result = runner.invoke(app, ["find"])
    assert result.exit_code == 0
    assert "transcript.jsonl" in result.output


def test_find_command_no_transcript(runner, monkeypatch):
    """Test find when no transcript exists."""
    from claude_parser.cli import app
    
    # Mock to return None
    monkeypatch.setattr("claude_parser.find_current_transcript", lambda: None)
    
    result = runner.invoke(app, ["find"])
    assert result.exit_code == 1
    assert "No transcript found" in result.output


def test_projects_command(runner, monkeypatch):
    """Test listing projects."""
    from claude_parser.cli import app
    
    # Mock project list
    mock_projects = [
        {"name": "project1", "original_path": "/path/to/project1"},
        {"name": "project2", "original_path": "/path/to/project2"}
    ]
    monkeypatch.setattr(
        "claude_parser.discovery.list_all_projects",
        lambda: mock_projects
    )
    
    result = runner.invoke(app, ["projects"])
    assert result.exit_code == 0
    assert "project1" in result.output
    assert "project2" in result.output


def test_export_command(runner, sample_jsonl):
    """Test export for semantic search."""
    from claude_parser.cli import app
    
    result = runner.invoke(app, ["export", sample_jsonl])
    assert result.exit_code == 0
    
    # Output should be valid JSON lines
    lines = result.output.strip().split('\n')
    for line in lines:
        if line and line.startswith('{'):  # Skip non-JSON lines
            data = json.loads(line)
            assert "text" in data or "content" in data


def test_export_with_no_tools(runner, sample_jsonl):
    """Test export with --no-tools flag."""
    from claude_parser.cli import app
    
    result = runner.invoke(app, ["export", sample_jsonl, "--no-tools"])
    assert result.exit_code == 0


def test_watch_command_mocked(runner, sample_jsonl, monkeypatch):
    """Test watch command with mocking."""
    from claude_parser.cli import app
    
    # Track if callback was called
    callback_called = []
    
    def mock_watch(file, callback, **kwargs):
        # Simulate calling the callback
        callback_called.append(True)
        # Create a mock conversation and messages
        class MockMessage:
            type = "user"
            text_content = "Test message content"
        
        callback(None, [MockMessage()])
    
    monkeypatch.setattr("claude_parser.watch.watch", mock_watch)
    
    result = runner.invoke(app, ["watch", sample_jsonl])
    assert callback_called  # Verify our mock was called
    assert "message" in result.output.lower()


def test_watch_with_uuid_checkpoint(runner, sample_jsonl, monkeypatch):
    """Test watch with --after-uuid option."""
    from claude_parser.cli import app
    
    uuid_received = []
    
    def mock_watch(file, callback, after_uuid=None, **kwargs):
        uuid_received.append(after_uuid)
        callback(None, [])
    
    monkeypatch.setattr("claude_parser.watch.watch", mock_watch)
    
    result = runner.invoke(app, ["watch", sample_jsonl, "--after-uuid", "test-uuid"])
    assert uuid_received[0] == "test-uuid"


def test_help_command(runner):
    """Test help output."""
    from claude_parser.cli import app
    
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Claude Parser" in result.output
    assert "parse" in result.output
    assert "export" in result.output
    assert "watch" in result.output