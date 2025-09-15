#!/usr/bin/env python3
"""
TDD test for get_text() extraction
Tests that messages with JSON content are properly extracted
@COMPOSITION: Tests plain dict utilities
"""

import pytest
from claude_parser.messages.utils import get_text


def test_assistant_message_text_extraction():
    """Test that get_text() extracts text from assistant JSON content"""
    # Message dict with JSON content structure
    msg = {
        'type': 'assistant',
        'content': '[{"type": "text", "text": "Perfect! Now Discord will show the actual message"}]'
    }
    
    # Should extract the actual text, not return the JSON string
    assert get_text(msg) == "Perfect! Now Discord will show the actual message"


def test_assistant_message_with_multiple_text_blocks():
    """Test extraction when there are multiple text blocks"""
    msg = {
        'type': 'assistant',
        'content': '[{"type": "text", "text": "First part."}, {"type": "text", "text": "Second part."}]'
    }
    
    # Should return first text block
    assert get_text(msg) == "First part."


def test_tool_use_content_handling():
    """Test that tool_use content is handled properly"""
    msg = {
        'type': 'assistant',
        'content': '[{"type": "tool_use", "name": "Write", "input": "data"}]'
    }
    
    # Should return empty string for tool_use content
    assert get_text(msg) == ""


def test_user_message_extraction():
    """Test that user messages are also extracted properly"""
    msg = {
        'type': 'user',
        'content': 'This is a user message'
    }
    
    # Should handle plain string content
    assert get_text(msg) == "This is a user message"


def test_plain_string_content():
    """Test that plain string content is returned as-is"""
    msg = {
        'type': 'user',
        'content': 'Simple string content'
    }
    
    assert get_text(msg) == "Simple string content"