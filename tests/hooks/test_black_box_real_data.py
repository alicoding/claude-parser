#!/usr/bin/env python3
"""
Black box tests using REAL hook data - @TDD_REAL_DATA
No mocking - just real data through real code paths
"""

import json
from .test_utils import create_hook_request, REAL_HOOK_SAMPLES


def test_posttooluse_with_real_data():
    """Test PostToolUse with real hook data structure"""
    # Use REAL data structure from Claude Code
    hook_data = REAL_HOOK_SAMPLES["PostToolUse"]

    # Create request the same way production does
    request = create_hook_request(hook_data)

    # Verify all fields are accessible
    assert request.hook_event_name == "PostToolUse"
    assert request.session_id == "abc-123"
    assert request.tool_name == "TodoWrite"
    assert request.tool_input["todos"][0]["content"] == "Fix bug"
    assert request.tool_response == "Todos updated successfully"


def test_pretooluse_with_real_data():
    """Test PreToolUse with real hook data structure"""
    hook_data = REAL_HOOK_SAMPLES["PreToolUse"]
    request = create_hook_request(hook_data)

    assert request.hook_event_name == "PreToolUse"
    assert request.tool_name == "Write"
    assert request.tool_input["file_path"] == "/test.py"


def test_complete_with_real_plugin_results():
    """Test complete() with real plugin result patterns"""
    hook_data = REAL_HOOK_SAMPLES["PostToolUse"]
    request = create_hook_request(hook_data)

    # Real plugin results pattern
    plugin_results = [
        ("allow", "✅ LOC check passed"),
        ("allow", "✅ Pattern check passed"),
        ("allow", None)  # Some plugins return no message
    ]

    # This is what lnca-hooks does
    exit_code = request.complete(plugin_results)

    assert exit_code == 0  # All allows = success


def test_complete_with_block_from_real_plugin():
    """Test ANY block = fail with real plugin patterns"""
    hook_data = REAL_HOOK_SAMPLES["PreToolUse"]
    request = create_hook_request(hook_data)

    # Real plugin block pattern from LOC validator
    plugin_results = [
        ("allow", "✅ Pattern check passed"),
        ("block", "🛡️ LNCA LOC VIOLATION: test.py has 120 lines (exceeds 80 LOC limit)"),
        ("allow", "✅ Memory check passed")
    ]

    exit_code = request.complete(plugin_results)

    assert exit_code == 2  # ANY block = exit code 2


def test_camelcase_and_snakecase_both_work():
    """Test that both Claude Code (camelCase) and tests (snake_case) work"""
    # Claude Code sends camelCase
    camel_data = {
        "hookEventName": "PostToolUse",
        "sessionId": "test-123",
        "transcriptPath": "/test.jsonl",
        "toolName": "Write"
    }

    # Tests might use snake_case
    snake_data = {
        "hook_event_name": "PostToolUse",
        "session_id": "test-123",
        "transcript_path": "/test.jsonl",
        "tool_name": "Write"
    }

    camel_request = create_hook_request(camel_data)
    snake_request = create_hook_request(snake_data)

    # Both should work
    assert camel_request.hook_event_name == "PostToolUse"
    assert snake_request.hook_event_name == "PostToolUse"
    assert camel_request.tool_name == "Write"
    assert snake_request.tool_name == "Write"