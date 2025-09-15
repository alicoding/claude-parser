#!/usr/bin/env python3
"""
Message Type Filtering Tests
@COMPOSITION: Tests dict-based filtering
"""

import pytest
from claude_parser import load_latest_session


def test_filter_by_type_user_messages():
    """Test filtering messages by type - @API_FIRST_TEST_DATA"""
    session_data = load_latest_session()
    if not session_data:
        pytest.skip("No session available for real data testing")
    
    messages = session_data.get('messages', [])
    
    # Filter to user messages using dict operations
    user_messages = [
        msg for msg in messages 
        if msg.get('type') == 'user' or msg.get('role') == 'user'
    ]
    
    # Verify we get real user messages from actual session
    assert isinstance(user_messages, list)
    if user_messages:
        for msg in user_messages:
            msg_type = msg.get('type') or msg.get('role')
            assert msg_type == 'user'


def test_filter_by_type_assistant_messages():
    """Test filtering assistant messages - @API_FIRST_TEST_DATA"""  
    session_data = load_latest_session()
    if not session_data:
        pytest.skip("No session available for real data testing")
    
    messages = session_data.get('messages', [])
    
    # Filter to assistant messages
    assistant_messages = [
        msg for msg in messages
        if msg.get('type') == 'assistant' or msg.get('role') == 'assistant'
    ]
    
    assert isinstance(assistant_messages, list)
    if assistant_messages:
        for msg in assistant_messages:
            msg_type = msg.get('type') or msg.get('role')
            assert msg_type == 'assistant'