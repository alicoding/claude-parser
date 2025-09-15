#!/usr/bin/env python3
"""
Hook Interface Tests: Black Box API Testing
@API_FIRST_TEST_DATA compliant - uses public execute_hook API only
"""

import pytest
from claude_parser.hooks import execute_hook, HookEvent

def test_execute_hook_accepts_required_fields():
    """Hook Test: execute_hook API accepts required Anthropic fields"""
    # Should not raise exceptions - black box behavior test
    execute_hook(
        hook_event_name="PreToolUse",
        session_id="test123",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/project"
    )

def test_execute_hook_supports_all_9_anthropic_hook_types():
    """Hook Test: API accepts all official Anthropic hook event types"""
    hook_types = [
        "PreToolUse", "PostToolUse", "UserPromptSubmit", "Notification",
        "Stop", "SubagentStop", "PreCompact", "SessionStart", "SessionEnd"
    ]
    
    for hook_type in hook_types:
        # Should not raise exceptions - black box behavior test
        execute_hook(
            hook_event_name=hook_type,
            session_id="test",
            transcript_path="/test.jsonl",
            cwd="/test"
        )

def test_execute_hook_handles_tool_fields():
    """Hook Test: API handles tool-specific fields for PreToolUse/PostToolUse"""
    # Should not raise exceptions - black box behavior test
    execute_hook(
        hook_event_name="PreToolUse",
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        tool_name="Write",
        tool_input='{"file_path": "/test.py", "content": "print(\'hello\')"}'
    )

def test_hook_enum_completeness():
    """Hook Test: HookEvent enum contains all required values"""
    # Test actual enum values directly - simpler and more reliable
    assert HookEvent.PRE_TOOL_USE == "PreToolUse"
    assert HookEvent.POST_TOOL_USE == "PostToolUse" 
    assert HookEvent.USER_PROMPT_SUBMIT == "UserPromptSubmit"
    assert HookEvent.NOTIFICATION == "Notification"
    assert HookEvent.STOP == "Stop"
    assert HookEvent.SUBAGENT_STOP == "SubagentStop"
    assert HookEvent.PRE_COMPACT == "PreCompact"
    assert HookEvent.SESSION_START == "SessionStart"
    assert HookEvent.SESSION_END == "SessionEnd"