#!/usr/bin/env python3
"""
Black Box Test: Message Content Extraction with None Values
Tests that get_message_content() handles None message fields correctly
"""

import pytest
from claude_parser import get_message_content, get_text


def test_message_none_bug_fixed():
    """Test that msg['message'] = None doesn't cause AttributeError

    This was the reported bug from claude-explorer where
    msg.get('message', {}).get('content', '') would fail
    """
    # The bug case: message key exists but is None
    msg = {'message': None}

    # Should not raise AttributeError
    content = get_message_content(msg)
    assert content == ''

    # Also test with get_text
    text = get_text(msg)
    assert text == ''


def test_message_content_safe_extraction():
    """Test safe extraction with various None scenarios"""
    test_cases = [
        ({'message': None}, ''),  # Bug case
        ({'content': 'direct'}, 'direct'),  # Direct content
        ({'message': {'content': 'nested'}}, 'nested'),  # Nested
        ({}, ''),  # Empty
        ({'content': None}, ''),  # Content is None
        ({'message': {}}, ''),  # Empty message dict
    ]

    for msg, expected in test_cases:
        assert get_message_content(msg) == expected


def test_content_block_extraction():
    """Test extraction from content blocks"""
    msg = {'content': [{'type': 'text', 'text': 'Block text'}]}
    assert get_message_content(msg) == 'Block text'

    # Empty blocks
    msg2 = {'content': []}
    assert get_message_content(msg2) == ''