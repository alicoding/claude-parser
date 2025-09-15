#!/usr/bin/env python3
"""
Blackbox TDD test for Discord message display bug
Tests the actual API as Discord plugin would use it
"""

import pytest
from claude_parser import load_session


def test_discord_shows_claude_text_not_json():
    """Test that Discord gets actual text, not JSON object"""
    # Load real session that Discord would load
    session_path = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser/2d2f54bd-6269-4023-8b1b-788b5f3e73e4.jsonl"
    session = load_session(session_path)
    
    assert session is not None, "Session should load"
    
    # What Discord plugin does
    latest_assistant = session.get_latest_assistant_message()
    assert latest_assistant is not None, "Should find assistant message"
    
    # Get the text as Discord would
    message_text = latest_assistant.get_text()
    
    # FAILURE CONDITION: Should NOT start with JSON array
    assert not message_text.startswith('[{'), f"Message should be text, not JSON. Got: {message_text[:100]}"
    
    # Should NOT contain JSON structure markers
    assert '"type": "text"' not in message_text, "Should extract text, not return JSON structure"
    
    # Should be actual readable text
    assert len(message_text) > 0, "Should have content"
    assert not message_text.startswith('['), "Should not start with array bracket"
    
    print(f"✓ Discord would correctly show: {message_text[:100]}...")


def test_sample_session_shows_correct_text():
    """Test with the sample session that has known content"""
    session_path = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser-tests-fixtures-sample-project/7cc6a4e8-eed1-4df4-8f40-b13b639d4a47.jsonl"
    session = load_session(session_path)
    
    assert session is not None
    
    # Get latest assistant message
    latest_assistant = session.get_latest_assistant_message()
    assert latest_assistant is not None
    
    text = latest_assistant.get_text()
    
    # Should show actual text about hello.py
    assert "hello" in text.lower() or "created" in text.lower(), f"Expected message about creating file, got: {text}"
    
    # Should NOT be JSON
    assert not text.startswith('[{'), "Should not be JSON array"
    
    print(f"✓ Sample session shows: {text}")


if __name__ == "__main__":
    print("Running blackbox tests for Discord message display...")
    print("=" * 60)
    
    try:
        test_discord_shows_claude_text_not_json()
        print("\n✓ Test 1 passed: Discord shows text, not JSON")
    except AssertionError as e:
        print(f"\n✗ Test 1 FAILED: {e}")
        
    print()
    
    try:
        test_sample_session_shows_correct_text()
        print("\n✓ Test 2 passed: Sample session shows correct text")
    except AssertionError as e:
        print(f"\n✗ Test 2 FAILED: {e}")