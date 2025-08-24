"""Test that exit_success outputs proper JSON for Claude Code."""

import pytest
import orjson
from claude_parser.hooks import exit_success


def test_exit_success_outputs_continue_json(capsys):
    """Test that exit_success outputs {"continue": true} for Claude Code."""
    # Act
    with pytest.raises(SystemExit) as exc_info:
        exit_success()
    
    # Assert - should exit with code 0
    assert exc_info.value.code == 0
    
    # Should output {"continue": true} to stdout
    captured = capsys.readouterr()
    output = orjson.loads(captured.out)
    assert output == {"continue": True}


def test_exit_success_with_message_outputs_json(capsys):
    """Test that exit_success with message still outputs valid JSON."""
    # Act
    with pytest.raises(SystemExit) as exc_info:
        exit_success("Additional info")
    
    # Assert
    assert exc_info.value.code == 0
    
    # Should output JSON with the message
    captured = capsys.readouterr()
    output = orjson.loads(captured.out)
    assert "continue" in output or "message" in output or "reason" in output