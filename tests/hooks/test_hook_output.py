#!/usr/bin/env python3
"""
Hook Interface Tests: Black Box API Testing with Real Data  
@API_FIRST_TEST_DATA compliant - uses public hook_success/hook_block API only
"""

def test_hook_success_with_real_session_data():
    """Hook Test: hook_success processes real session data without errors"""
    from claude_parser import load_latest_session  
    from claude_parser.hooks import hook_success
    
    # Use public API to get real session data
    session = load_latest_session()
    if not session:
        hook_success("No session available - testing basic API")
        return
        
    # Use real session context - black box test
    hook_success(f"Processed session {session.session_id} successfully")

def test_hook_block_with_real_session_analysis():
    """Hook Test: hook_block processes real session analysis data"""
    from claude_parser import load_latest_session
    from claude_parser.hooks import hook_block
    import pytest
    
    # Use public API to get session context
    session = load_latest_session()
    session_info = f"session {session.session_id}" if session else "test session"
    
    # Test hook_block - should raise SystemExit with code 2
    with pytest.raises(SystemExit) as exc_info:
        hook_block(f"Blocking operation for {session_info} due to validation failure")
    
    # Verify proper Anthropic exit code
    assert exc_info.value.code == 2

def test_hook_error_handling():
    """Hook Test: hook_error handles error conditions properly"""
    from claude_parser.hooks import hook_error
    import pytest
    
    # Test hook_error - should raise SystemExit with code 1  
    with pytest.raises(SystemExit) as exc_info:
        hook_error("Test error condition")
    
    # Verify proper error exit code
    assert exc_info.value.code == 1