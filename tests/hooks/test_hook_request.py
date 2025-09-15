#!/usr/bin/env python3
"""
Test HookRequest API - @TDD_REAL_DATA @API_FIRST_TEST_DATA
Black box testing with real hook data
"""

import json
import sys
from io import StringIO
from unittest.mock import patch
import pytest


def test_hook_request_with_real_jsonl():
    """Test HookRequest parses real hook input"""
    from claude_parser.hooks import HookRequest
    
    # Real PreToolUse input from Anthropic
    hook_input = {
        "session_id": "abc123",
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {
            "file_path": "/test.py",
            "content": "print('hello')"
        }
    }
    
    # Use parse_hook_input like production code
    with patch('sys.stdin', StringIO(json.dumps(hook_input))):
        from claude_parser.hooks import parse_hook_input
        hook_data = parse_hook_input()
        request = HookRequest(hook_data)
        
        assert request.session_id == "abc123"
        assert request.hook_event_name == "PreToolUse"
        assert request.tool_name == "Write"
        assert request.tool_input["file_path"] == "/test.py"


def test_complete_with_all_allows():
    """Test complete() with all plugins allowing"""
    from claude_parser.hooks import HookRequest
    
    # Setup request
    hook_input = {
        "hook_event_name": "PostToolUse",
        "session_id": "test",
        "transcript_path": "/test.jsonl"
    }
    
    # Use parse_hook_input like production code
    with patch('sys.stdin', StringIO(json.dumps(hook_input))):
        from claude_parser.hooks import parse_hook_input
        hook_data = parse_hook_input()
        request = HookRequest(hook_data)
    
    # All plugins allow
    results = [
        ("allow", "Context from plugin 1"),
        ("allow", "Context from plugin 2"),
        ("allow", None),  # Allow with no message
    ]
    
    # Capture output
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        exit_code = request.complete(results)
    
    assert exit_code == 0
    output = mock_stdout.getvalue()
    if output:
        parsed = json.loads(output)
        assert "Context from plugin 1" in str(parsed)
        assert "Context from plugin 2" in str(parsed)


def test_complete_with_one_block_four_allows():
    """Test ANY block = whole fail policy"""
    from claude_parser.hooks import HookRequest
    
    hook_input = {
        "hook_event_name": "PreToolUse", 
        "session_id": "test",
        "transcript_path": "/test.jsonl"
    }
    
    # Use parse_hook_input like production code
    with patch('sys.stdin', StringIO(json.dumps(hook_input))):
        from claude_parser.hooks import parse_hook_input
        hook_data = parse_hook_input()
        request = HookRequest(hook_data)
    
    # 1 block + 4 allows = BLOCK
    results = [
        ("allow", "Good to go"),
        ("block", "Security violation detected"),  # This causes whole fail
        ("allow", "Looks fine"),
        ("allow", "No issues"),
        ("allow", None),
    ]
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        exit_code = request.complete(results)
    
    assert exit_code == 2  # Block exit code
    output = mock_stdout.getvalue()
    parsed = json.loads(output)
    assert "Security violation detected" in str(parsed)


def test_complete_with_multiple_blocks():
    """Test multiple blocks are all included in output"""
    from claude_parser.hooks import HookRequest
    
    hook_input = {
        "hook_event_name": "PreToolUse",
        "session_id": "test", 
        "transcript_path": "/test.jsonl"
    }
    
    # Use parse_hook_input like production code
    with patch('sys.stdin', StringIO(json.dumps(hook_input))):
        from claude_parser.hooks import parse_hook_input
        hook_data = parse_hook_input()
        request = HookRequest(hook_data)
    
    # Multiple blocks
    results = [
        ("block", "LOC violation: 120 lines"),
        ("allow", "Memory OK"),
        ("block", "Critical file needs approval"),
        ("block", "Pattern violation detected"),
    ]
    
    with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
        exit_code = request.complete(results)
    
    assert exit_code == 2
    output = mock_stdout.getvalue()
    
    # All block reasons should be in output
    assert "LOC violation" in output
    assert "Critical file" in output
    assert "Pattern violation" in output


def test_all_hook_event_types():
    """Test HookRequest handles all hook types correctly"""
    from claude_parser.hooks import HookRequest
    
    hook_types = [
        "PreToolUse", "PostToolUse", "UserPromptSubmit",
        "Stop", "SubagentStop", "Notification",
        "PreCompact", "SessionStart", "SessionEnd"
    ]
    
    for hook_type in hook_types:
        hook_input = {
            "hook_event_name": hook_type,
            "session_id": "test",
            "transcript_path": "/test.jsonl"
        }
        
        with patch('sys.stdin', StringIO(json.dumps(hook_input))):
            request = HookRequest.from_stdin()
            assert request.hook_event_name == hook_type
            
            # Should handle empty results
            exit_code = request.complete([])
            assert exit_code == 0