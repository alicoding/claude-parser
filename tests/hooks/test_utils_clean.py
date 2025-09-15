#!/usr/bin/env python3
"""
Test utilities for hook testing - @DRY @UTIL_FIRST @NO_MOCKING
Single source of truth for getting real hook data
"""

from typing import Dict, Any, List, Optional
from claude_parser.hooks import HookRequest


def create_hook_request(hook_data: Dict[str, Any]) -> HookRequest:
    """Create HookRequest from test data - @SINGLE_SOURCE_TRUTH

    This is how ALL tests should create HookRequest objects.
    Just pass the data directly - no mocking needed!
    """
    return HookRequest(hook_data)


def get_real_hook_events_from_session(session_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get REAL hook events from a session using our SDK - @DOGFOODING

    Uses our own SDK to get real hook events from transcripts.
    This is TRUE black box testing - using our own tools!
    """
    from claude_parser import load_session, load_latest_session

    # Load session using our SDK
    if session_path:
        session = load_session(session_path)
    else:
        session = load_latest_session()

    if not session:
        return []

    # Find all hook events in the session
    hook_events = []
    for msg in session.get('messages', []):
        # Hook events have hookEventName field (Claude Code format)
        if msg.get('hookEventName') or msg.get('hook_event_name'):
            hook_events.append(msg)

    return hook_events


# Real hook data structure from Claude Code (for reference)
CLAUDE_CODE_HOOK_FORMAT = {
    "PostToolUse": {
        "hookEventName": "PostToolUse",  # camelCase from Claude Code
        "sessionId": "abc-123",
        "transcriptPath": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "toolName": "TodoWrite",
        "toolInput": {
            "todos": [
                {"content": "Fix bug", "status": "pending", "activeForm": "Fixing bug"}
            ]
        },
        "toolResponse": "Todos updated successfully"
    },
    "PreToolUse": {
        "hookEventName": "PreToolUse",
        "sessionId": "def-456",
        "transcriptPath": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "toolName": "Write",
        "toolInput": {
            "file_path": "/test.py",
            "content": "print('hello world')"
        }
    }
}