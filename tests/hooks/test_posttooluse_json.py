#!/usr/bin/env python3
"""
Test PostToolUse always outputs JSON - TDD for bug fix
@TDD_REAL_DATA: Test with real hook scenarios
"""

import json
from claude_parser.hooks.aggregator import aggregate_results


def test_posttooluse_with_no_messages_outputs_json():
    """PostToolUse with no plugin messages should still output JSON"""
    # Empty results (all plugins said allow with no message)
    results = []

    output, exit_code = aggregate_results("PostToolUse", results)

    # Should output JSON even with no messages
    assert output is not None, "PostToolUse must always output JSON"
    assert exit_code == 0

    # Verify it's valid JSON
    parsed = json.loads(output)
    assert "hookSpecificOutput" in parsed
    assert parsed["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert parsed["hookSpecificOutput"]["additionalContext"] == ""


def test_posttooluse_with_allow_messages_outputs_json():
    """PostToolUse with allow messages outputs proper JSON"""
    results = [
        ("allow", "Check 1 passed"),
        ("allow", "Check 2 passed")
    ]

    output, exit_code = aggregate_results("PostToolUse", results)

    assert output is not None
    assert exit_code == 0

    parsed = json.loads(output)
    assert parsed["hookSpecificOutput"]["additionalContext"] == "Check 1 passed\nCheck 2 passed"


def test_posttooluse_with_block_outputs_json():
    """PostToolUse with block outputs proper JSON"""
    results = [
        ("allow", "Check 1 passed"),
        ("block", "Violation detected")
    ]

    output, exit_code = aggregate_results("PostToolUse", results)

    assert output is not None
    assert exit_code == 2  # Block exit code

    parsed = json.loads(output)
    assert "decision" in parsed or "hookSpecificOutput" in parsed


def test_pretooluse_allow_without_message_returns_none():
    """PreToolUse with no messages returns None (current behavior)"""
    results = []

    output, exit_code = aggregate_results("PreToolUse", results)

    # PreToolUse returns None when no context
    assert output is None
    assert exit_code == 0