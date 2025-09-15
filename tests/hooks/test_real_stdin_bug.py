#!/usr/bin/env python3
"""
Test REAL stdin format from Claude Code - TDD for the bug
@TDD_REAL_DATA: Using actual Claude Code format
"""

import json
from io import StringIO
from unittest.mock import patch


def test_hookeventname_camelcase_from_claude_code():
    """Claude Code sends hookEventName in camelCase, not snake_case"""
    from claude_parser.hooks import HookRequest

    # ACTUAL format from Claude Code (camelCase)
    actual_claude_input = {
        "hookEventName": "PostToolUse",  # <-- This is what Claude sends!
        "sessionId": "abc123",
        "transcriptPath": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "toolName": "Write",
        "toolInput": {
            "file_path": "/test.py",
            "content": "print('hello')"
        }
    }

    with patch('sys.stdin', StringIO(json.dumps(actual_claude_input))):
        request = HookRequest.from_stdin()

        # This will FAIL because HookRequest expects hook_event_name
        assert request.hook_event_name == "PostToolUse", f"Got: {request.hook_event_name}"

        # These will also fail
        assert request.session_id != "", f"session_id not set: {request.session_id}"
        assert request.transcript_path != "", f"transcript_path not set: {request.transcript_path}"