#!/usr/bin/env python3
"""
Test get_latest_assistant_message with REAL data
@TDD_REAL_DATA: Uses actual JSONL file
"""

from claude_parser import load_session
from claude_parser.navigation import get_latest_assistant_message


def test_get_latest_assistant_message_with_tools():
    """Test that we can get assistant message even when it uses tools"""
    # Use the real test JSONL we know exists
    test_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-real-jsonl-data-for-claude-parser/2f97e0b9-c2ff-4915-b682-60510a72ca57.jsonl"

    session = load_session(test_file)
    assert session is not None

    messages = session.get('messages', [])
    assert len(messages) > 0

    # Get latest assistant message
    latest = get_latest_assistant_message(messages)

    # Should return something, not None
    assert latest is not None, "get_latest_assistant_message returned None"
    assert latest.get('type') == 'assistant'

    # Print for debugging if needed
    content = str(latest.get('content', ''))[:100]
    print(f"Got assistant message: {content}...")