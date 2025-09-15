#!/usr/bin/env python3
"""
Hook Interface Tests: Real Claude Hook Data - PreToolUse
100% framework delegation: Use real hook data extracted from current session
"""

import pytest
import json
import io
from unittest.mock import patch
from claude_parser import load_latest_session

@pytest.fixture
def real_hook_base():
    """Extract real hook data structure using @API_FIRST_TEST_DATA pattern"""
    session = load_latest_session()
    if not session:
        pytest.skip("No Claude session available")
    
    # Use public API to discover session files - @API_FIRST_TEST_DATA compliant
    from claude_parser import discover_current_project_files
    session_files = discover_current_project_files()
    if not session_files:
        pytest.skip("No session files found via discovery API")
    
    # Use the first available session file 
    transcript_path = str(session_files[0])
    
    return {
        'session_id': session.session_id,
        'transcript_path': transcript_path,
        'cwd': session.metadata.get('cwd', '/tmp'),
    }

def test_extract_real_hook_events_from_session():
    """Hook Test: Extract real hook events using fluent API - @API_FIRST_TEST_DATA compliant"""
    from claude_parser import load_latest_session
    
    # Use fluent API to get real hook events
    conversation = load_latest_session()
    if not conversation:
        return  # Skip if no session available
    
    # Test the fluent API - zero hardcoding, 100% real data
    hook_events = conversation.get_hook_events()
    
    # Verify we get real hook events from the actual session JSONL
    assert isinstance(hook_events, list)
    if hook_events:  # If any events found
        event = hook_events[0]
        assert 'hook_event_name' in event
        assert 'session_id' in event  
        assert 'transcript_path' in event
        assert 'cwd' in event
        # All data should be real, not hardcoded
        assert event['session_id'] != 'unknown'
        assert not event['transcript_path'].startswith('/api/')  # No hardcoded paths