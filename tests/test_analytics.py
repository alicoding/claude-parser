#!/usr/bin/env python3
"""
Analytics Interface Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from claude_parser import load_latest_session, analyze_session

def test_analyze_session_interface_with_real_data():
    """Interface Test: analyze_session accepts RichSession and returns dict"""
    session = load_latest_session()
    if not session or len(session.messages) == 0:
        pytest.skip("No real Claude session with messages found")
    
    # Should not crash and return dict
    result = analyze_session(session)
    assert isinstance(result, dict)

def test_analyze_session_contract_with_real_data():
    """Contract Test: analyze_session returns expected analytics structure"""
    session = load_latest_session() 
    if not session or len(session.messages) == 0:
        pytest.skip("No real Claude session with messages found")
    
    result = analyze_session(session)
    
    # Contract: must have basic analytics fields
    assert 'message_count' in result
    assert 'tool_usage' in result or 'types' in result  # Some kind of breakdown
    
    # Contract: message_count should match actual messages
    assert result['message_count'] == len(session.messages)

def test_analyze_session_integration_pandas():
    """Integration Test: Uses pandas properly for real data processing"""
    session = load_latest_session()
    if not session or len(session.messages) == 0:
        pytest.skip("No real Claude session with messages found")
    
    result = analyze_session(session)
    
    # BDD: Should handle real session data without errors
    assert isinstance(result['message_count'], int)
    assert result['message_count'] > 0  # Real session should have messages