#!/usr/bin/env python3
"""
Test utilities for hook testing - @DRY @UTIL_FIRST
Single source of truth for hook test patterns
"""

import json
from io import StringIO
from unittest.mock import patch
from typing import Dict, Any, List
from claude_parser.hooks import HookRequest, parse_hook_input

# Real hook data samples for testing
REAL_HOOK_SAMPLES = {
    "PostToolUse": {
        "hookEventName": "PostToolUse",
        "sessionId": "abc-123",
        "transcriptPath": "/test.jsonl",
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
        "transcriptPath": "/test.jsonl",
        "toolName": "Write",
        "toolInput": {
            "file_path": "/test.py",
            "content": "# Test content"
        }
    }
}


def create_hook_request(hook_data: Dict[str, Any]) -> HookRequest:
    """Create HookRequest from test data - @SINGLE_SOURCE_TRUTH

    This is how ALL tests should create HookRequest objects.
    Just pass the data directly - no mocking needed!
    """
    return HookRequest(hook_data)


def get_real_hook_data_from_current_session() -> List[Dict[str, Any]]:
    """Get REAL hook data from current session using our SDK - @DOGFOODING

    Uses our own SDK to get real hook events from the current transcript.
    This is TRUE black box testing - using our own tools!
    """
    from claude_parser import load_latest_session

    # Get current session using our SDK
    session = load_latest_session()
    if not session:
        return []

    # Find all hook events in the session
    hook_events = []
    for msg in session.get('messages', []):
        # Hook events have hookEventName field
        if msg.get('hookEventName') or msg.get('hook_event_name'):
            hook_events.append(msg)

    return hook_events




def get_real_hook_data_from_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Get REAL hook data from a specific transcript - @DOGFOODING

    When HookRequest has transcript_path, we can load the actual session!
    """
    from claude_parser import load_session

    session = load_session(transcript_path)
    if not session:
        return []

    hook_events = []
    for msg in session.get('messages', []):
        if msg.get('hookEventName') or msg.get('hook_event_name'):
            hook_events.append(msg)

    return hook_events