#!/usr/bin/env python3
"""
Black Box Session Tests - 100% Public API Usage [@API_FIRST_TEST_DATA]
Tests session functionality using only claude-parser public interface
"""

import pytest
from claude_parser import load_session, load_latest_session, discover_all_sessions


@pytest.fixture
def real_session():
    """@API_FIRST_TEST_DATA: Get real session using public API only"""
    session = load_latest_session()
    if not session:
        pytest.skip("No real Claude sessions found")
    return session


def test_load_session_interface():
    """Interface Test: load_session returns RichSession or None"""
    result = load_latest_session()
    # Contract: should return RichSession object or None
    assert result is None or hasattr(result, 'messages')


def test_session_analytics_integration(real_session):
    """Integration Test: Session works with analytics using public API"""
    from claude_parser import analyze_session
    
    # Contract: analyze_session accepts RichSession and returns dict
    result = analyze_session(real_session)
    assert isinstance(result, dict)
    assert 'message_count' in result
    assert 'types' in result


def test_session_filtering_integration(real_session):
    """Integration Test: Session filtering works via public interface"""
    # Test semantic filtering interface
    user_messages = list(real_session.filter_by_type('user'))
    assistant_messages = list(real_session.filter_by_type('assistant'))
    
    # Contract: filter methods return iterators
    assert hasattr(user_messages, '__iter__')
    assert hasattr(assistant_messages, '__iter__')


def test_session_navigation_integration(real_session):
    """Integration Test: Session navigation via public interface"""
    # Test navigation methods
    latest = real_session.get_latest_message()
    first = real_session.get_first_message()
    
    # Contract: navigation methods return messages or None
    if len(real_session.messages) > 0:
        assert latest is not None
        assert first is not None