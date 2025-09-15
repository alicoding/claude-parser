#!/usr/bin/env python3
"""
Timeline Summary Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from claude_parser import load_latest_session, get_timeline_summary


@pytest.fixture
def real_session():
    """Real Data: Use discovered Claude session for timeline testing"""
    session = load_latest_session()
    if not session or len(session.messages) == 0:
        pytest.skip("No real Claude session with messages found")
    return session


def test_get_timeline_summary_integration_real_data(real_session):
    """Integration Test: get_timeline_summary analyzes real session data"""
    result = get_timeline_summary(real_session)
    
    # Contract: should return dict with expected keys
    assert isinstance(result, dict)
    assert 'total_messages' in result
    assert 'types' in result
    assert 'uuids' in result
    
    # Integration: Real data should have meaningful values
    assert result['total_messages'] > 0
    assert isinstance(result['types'], dict)
    assert isinstance(result['uuids'], list)


def test_timeline_summary_contract_validation(real_session):
    """Contract Test: Timeline summary has correct data types"""
    result = get_timeline_summary(real_session)
    
    # BDD: Summary should provide useful analytics
    assert isinstance(result['total_messages'], int)
    assert result['total_messages'] == len(real_session.messages)
    
    # Contract: Types should be message type counts
    for msg_type, count in result['types'].items():
        assert isinstance(msg_type, str)
        assert isinstance(count, int)
        assert count > 0


def test_timeline_summary_error_handling():
    """Contract Test: Summary handles invalid inputs gracefully"""  
    # BDD: None session should return empty summary
    result = get_timeline_summary(None)
    expected = {'total_messages': 0, 'types': {}, 'uuids': []}
    assert result == expected


def test_empty_session_summary():
    """BDD Test: Empty session produces empty summary"""
    from claude_parser.models import RichSession
    
    empty_session = RichSession(
        session_id="empty_test",
        messages=[],
        metadata={},
        raw_data=[]
    )
    
    result = get_timeline_summary(empty_session)
    assert result['total_messages'] == 0
    assert result['types'] == {}
    assert result['uuids'] == []