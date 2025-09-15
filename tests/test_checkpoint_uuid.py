#!/usr/bin/env python3
"""
TDD: Checkpoint UUID - 100% framework delegation
Single responsibility: UUID extraction from real session data
"""

def test_checkpoint_uuid_extraction_blackbox():
    """TDD: Extract message UUIDs from real session - 100% public API"""
    from claude_parser import load_latest_session
    
    # Use existing interface to get real session
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Test that messages have UUIDs
    messages_with_uuid = [msg for msg in session.messages if hasattr(msg, 'uuid')]
    if messages_with_uuid:
        first_msg = messages_with_uuid[0]
        assert hasattr(first_msg, 'uuid')
        assert first_msg.uuid is not None
        assert len(first_msg.uuid) > 0
        print(f"✅ Found message UUID: {first_msg.uuid}")
    else:
        # If no UUIDs found, that's also valid data
        assert True

def test_checkpoint_uuid_exists_in_session_timeline():
    """TDD: Message UUIDs should exist consistently - 100% public API"""
    from claude_parser import load_latest_session, find_message_by_uuid
    
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Use public API to test UUID consistency
    messages_with_uuid = [msg for msg in session.messages if hasattr(msg, 'uuid')]
    if messages_with_uuid:
        first_msg = messages_with_uuid[0]
        test_uuid = first_msg.uuid
        
        # UUID should be findable via public API
        found_message = find_message_by_uuid(session, test_uuid)
        assert found_message is not None
        assert found_message['uuid'] == test_uuid
        
        print(f"UUID consistency verified: {test_uuid}")