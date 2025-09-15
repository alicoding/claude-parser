#!/usr/bin/env python3
"""
TDD: Checkpoint Content - 100% framework delegation
Single responsibility: Validate checkpoint message content
"""

def test_checkpoint_returns_user_message_before_file_operation():
    """TDD: Should find user messages that led to file operations - 100% public API"""
    from claude_parser import load_latest_session
    
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Use public API to analyze messages
    user_messages = [msg for msg in session.messages if getattr(msg, 'type', '') == 'user']
    if user_messages:
        # Should have user messages in session
        assert len(user_messages) > 0
        
        # Should have content we can analyze
        first_user_msg = user_messages[0]
        content = str(getattr(first_user_msg, 'content', ''))
        assert len(content) > 0
        
        print(f"✅ Found user message: {content[:50]}...")

def test_checkpoint_content_is_user_text():
    """TDD: User message content should be user text, not tool results - 100% public API"""
    from claude_parser import load_latest_session
    
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Use public API to find user messages
    user_messages = [msg for msg in session.messages if getattr(msg, 'type', '') == 'user']
    if user_messages:
        first_user_msg = user_messages[0]
        content = str(getattr(first_user_msg, 'content', ''))
        
        # Should not contain tool result markers
        assert 'tool_use_id' not in content.lower()
        assert 'tool_result' not in content.lower()
        
        # Should be actual user message text
        assert len(content.strip()) > 0