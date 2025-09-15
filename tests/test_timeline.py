#!/usr/bin/env python3
"""
Timeline Interface Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from claude_parser import load_latest_session, find_message_by_uuid, get_message_sequence


@pytest.fixture
def real_session():
    """Real Data: Use discovered Claude session for timeline testing"""
    session = load_latest_session()
    if not session or len(session.messages) == 0:
        pytest.skip("No real Claude session with messages found")
    return session


def test_find_message_by_uuid_interface_contract(real_session):
    """Interface Test: find_message_by_uuid accepts session and UUID string"""
    first_message = real_session.messages[0]
    if not hasattr(first_message, 'uuid'):
        pytest.skip("Real session messages don't have UUID field")
    
    result = find_message_by_uuid(real_session, first_message.uuid)
    
    # Contract: should return dict or None
    assert result is None or isinstance(result, dict)
    if result:
        assert 'uuid' in result and 'type' in result


def test_get_message_sequence_contract_real_data(real_session):
    """Contract Test: get_message_sequence works with real session UUIDs"""
    if len(real_session.messages) < 2:
        pytest.skip("Need at least 2 messages for sequence test")
    
    # Use real UUIDs from session
    messages_with_uuids = [msg for msg in real_session.messages if hasattr(msg, 'uuid')]
    if len(messages_with_uuids) < 2:
        pytest.skip("Need at least 2 messages with UUIDs")
    
    start_uuid = messages_with_uuids[0].uuid
    end_uuid = messages_with_uuids[1].uuid
    
    result = get_message_sequence(real_session, start_uuid, end_uuid)
    
    # Contract: should return list of dicts
    assert isinstance(result, list)
    for msg in result:
        assert isinstance(msg, dict)
        assert 'uuid' in msg and 'type' in msg


def test_timeline_navigation_error_handling():
    """Contract Test: Navigation functions handle invalid inputs gracefully"""
    # BDD: None session should not crash
    result = find_message_by_uuid(None, "test-uuid")
    assert result is None
    
    result = get_message_sequence(None, "uuid1", "uuid2")
    assert result == []