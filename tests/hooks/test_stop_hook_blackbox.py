#!/usr/bin/env python3
"""
Black box test for Discord stop hook bug using REAL data
@TDD_REAL_DATA: Uses real JSONL production data
@API_FIRST_TEST_DATA: Tests through public API only
@LOC_ENFORCEMENT: <80 LOC
"""

from pathlib import Path
from claude_parser.hooks.request import HookRequest


def test_stop_hook_with_real_jsonl_data():
    """Test stop hook with real JSONL data returns plain text"""
    # Use real JSONL test data
    test_data_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/")

    # Use the 78k file for faster testing
    jsonl_path = test_data_dir / "3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl"
    assert jsonl_path.exists(), f"Test JSONL not found: {jsonl_path}"

    # Simulate stop hook as Discord would call it
    hook_data = {
        "hookEventName": "stop",
        "sessionId": "test-session",
        "transcriptPath": str(jsonl_path),
        "cwd": str(Path.cwd())
    }

    request = HookRequest(hook_data)
    latest_message = request.get_latest_claude_message()

    # API should return plain text string, not complex object
    assert latest_message is not None, "get_latest_claude_message() returned None"
    assert isinstance(latest_message, str), f"Expected string, got {type(latest_message)}: {latest_message}"

    # Should contain actual text, not JSON structure
    assert not latest_message.startswith('[{"type"'), f"Got JSON structure instead of plain text: {latest_message}"
    assert not latest_message.startswith('{"type"'), f"Got JSON object instead of plain text: {latest_message}"

    # Should have actual content
    assert len(latest_message) > 0, "Got empty string"
    print(f"✅ API returned plain text: {latest_message[:100]}...")


def test_filter_real_hook_events():
    """Test filtering hook events from real session"""
    session = load_latest_session()
    assert session is not None

    # Get hook events from the session
    hook_events = session.get('hook_events', [])

    # Filter for Stop hooks
    stop_hooks = list(filter_hook_events_by_type(hook_events, 'Stop'))

    # Verify we can find Stop hooks
    if stop_hooks:
        first_stop = stop_hooks[0]
        assert 'hook_event_name' in first_stop or 'hookEventName' in first_stop