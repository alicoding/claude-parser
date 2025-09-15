#!/usr/bin/env python3
"""
Test HookRequest API - @TDD_REAL_DATA @API_FIRST_TEST_DATA
Black box testing with real hook data - NO MOCKING
"""

import json
from claude_parser.hooks import HookRequest


def test_hook_request_with_real_data():
    """Test HookRequest with real hook data structure - no mocking"""
    # Real PreToolUse data structure from Claude Code
    hook_data = {
        "sessionId": "abc123",  # Claude Code sends camelCase
        "transcriptPath": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hookEventName": "PreToolUse",
        "toolName": "Write",
        "toolInput": {
            "file_path": "/test.py",
            "content": "print('hello')"
        }
    }

    # Direct instantiation - no mocking
    request = HookRequest(hook_data)

    assert request.session_id == "abc123"
    assert request.hook_event_name == "PreToolUse"
    assert request.tool_name == "Write"
    assert request.tool_input["file_path"] == "/test.py"


def test_complete_with_all_allows():
    """Test complete() with all plugins allowing - no mocking"""
    # Real PostToolUse data
    hook_data = {
        "hookEventName": "PostToolUse",
        "sessionId": "test",
        "transcriptPath": "/test.jsonl"
    }

    request = HookRequest(hook_data)

    # Real plugin results pattern
    results = [
        ("allow", "Context from plugin 1"),
        ("allow", "Context from plugin 2"),
        ("allow", None),  # Allow with no message
    ]

    # Complete returns exit code
    exit_code = request.complete(results)
    assert exit_code == 0


def test_complete_with_one_block():
    """Test ANY block = whole fail policy - no mocking"""
    hook_data = {
        "hookEventName": "PreToolUse",
        "sessionId": "test",
        "transcriptPath": "/test.jsonl"
    }

    request = HookRequest(hook_data)

    # 1 block + 4 allows = BLOCK
    results = [
        ("allow", "Good to go"),
        ("block", "Security violation detected"),  # This causes whole fail
        ("allow", "Looks fine"),
        ("allow", "No issues"),
        ("allow", None),
    ]

    exit_code = request.complete(results)
    assert exit_code == 2  # Block exit code


def test_complete_with_multiple_blocks():
    """Test multiple blocks are all included - no mocking"""
    hook_data = {
        "hookEventName": "PreToolUse",
        "sessionId": "test",
        "transcriptPath": "/test.jsonl"
    }

    request = HookRequest(hook_data)

    # Multiple blocks
    results = [
        ("block", "LOC violation: 120 lines"),
        ("allow", "Memory OK"),
        ("block", "Critical file needs approval"),
        ("block", "Pattern violation detected"),
    ]

    exit_code = request.complete(results)
    assert exit_code == 2


def test_all_hook_event_types():
    """Test HookRequest handles all hook types - no mocking"""
    hook_types = [
        "PreToolUse", "PostToolUse", "UserPromptSubmit",
        "Stop", "SubagentStop", "Notification",
        "PreCompact", "SessionStart", "SessionEnd"
    ]

    for hook_type in hook_types:
        hook_data = {
            "hookEventName": hook_type,
            "sessionId": "test",
            "transcriptPath": "/test.jsonl"
        }

        request = HookRequest(hook_data)
        assert request.hook_event_name == hook_type

        # Should handle empty results
        exit_code = request.complete([])
        # PostToolUse always outputs JSON, so exit code is 0
        assert exit_code == 0


def test_camelcase_and_snakecase_compatibility():
    """Test both camelCase (Claude Code) and snake_case work"""
    # Claude Code sends camelCase
    camel_data = {
        "hookEventName": "PostToolUse",
        "sessionId": "test-123",
        "transcriptPath": "/test.jsonl",
        "toolName": "Write",
        "toolInput": {"file_path": "test.py"}
    }

    # Some tests might use snake_case
    snake_data = {
        "hook_event_name": "PostToolUse",
        "session_id": "test-123",
        "transcript_path": "/test.jsonl",
        "tool_name": "Write",
        "tool_input": {"file_path": "test.py"}
    }

    camel_request = HookRequest(camel_data)
    snake_request = HookRequest(snake_data)

    # Both should work
    assert camel_request.hook_event_name == "PostToolUse"
    assert snake_request.hook_event_name == "PostToolUse"
    assert camel_request.tool_name == "Write"
    assert snake_request.tool_name == "Write"