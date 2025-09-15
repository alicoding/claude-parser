#!/usr/bin/env python3
"""
TDD: cg command tests - Start with RED (failing) tests
@TDD_REAL_DATA: Use actual conversation data
@PAIR_PROGRAMMING: One file at a time
"""

from subprocess import run
from pathlib import Path
import pytest


def test_cg_checkout_file_not_implemented():
    """RED: cg checkout <file> should restore file from JSONL"""
    # This will FAIL until we implement the command
    result = run(['python', '-m', 'claude_parser.cli.cg', 'checkout', 'test.py'],
                 capture_output=True, text=True)

    # Expecting this to work (will fail for now)
    assert "Restored" in result.stdout or "No checkpoint" in result.stdout
    assert result.returncode == 0


def test_cg_reset_hard_not_implemented():
    """RED: cg reset --hard should restore to checkpoint"""
    # This will FAIL until implemented
    result = run(['python', '-m', 'claude_parser.cli.cg', 'reset', '--hard', 'some-uuid'],
                 capture_output=True, text=True)

    assert result.returncode == 0


def test_cg_revert_not_implemented():
    """RED: cg revert should undo a specific change"""
    # This will FAIL until implemented
    result = run(['python', '-m', 'claude_parser.cli.cg', 'revert', 'some-uuid'],
                 capture_output=True, text=True)

    assert result.returncode == 0


def test_with_real_conversation_data():
    """Use THIS actual conversation's JSONL"""
    from claude_parser import load_latest_session

    session = load_latest_session()
    assert session is not None, "Should load current session"

    # Check we have messages with tools
    tool_messages = [m for m in session.get('messages', [])
                     if 'tool_use' in str(m)]
    assert len(tool_messages) > 0, "Should have tool operations in this conversation"