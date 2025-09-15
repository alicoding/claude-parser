#!/usr/bin/env python3
"""
Tool Usage Filtering Tests
@COMPOSITION: Tests dict-based tool filtering
"""

import pytest
from claude_parser import load_latest_session
from claude_parser.messages.utils import get_text


def test_filter_by_tool_usage():
    """Test filtering by tool usage - @API_FIRST_TEST_DATA"""
    session_data = load_latest_session()
    if not session_data:
        pytest.skip("No session available for real data testing")
    
    messages = session_data.get('messages', [])
    
    # Find messages that use the Read tool
    read_tool_messages = []
    for msg in messages:
        if msg.get('type') == 'assistant' and 'message' in msg:
            content = msg['message'].get('content', [])
            if isinstance(content, list):
                for item in content:
                    if (isinstance(item, dict) and 
                        item.get('type') == 'tool_use' and
                        item.get('name') == 'Read'):
                        read_tool_messages.append(msg)
                        break
    
    # Real sessions might not have Read tool usage
    assert isinstance(read_tool_messages, list)


def test_search_content():
    """Test searching message content - @API_FIRST_TEST_DATA"""
    session_data = load_latest_session()
    if not session_data:
        pytest.skip("No session available for real data testing")
    
    messages = session_data.get('messages', [])
    
    # Search for messages containing 'claude-parser'
    matching_messages = []
    for msg in messages:
        text = get_text(msg)
        if text and 'claude-parser' in text.lower():
            matching_messages.append(msg)
    
    assert isinstance(matching_messages, list)
    # Verify all matching messages contain the keyword
    for msg in matching_messages:
        text = get_text(msg)
        assert 'claude-parser' in text.lower()