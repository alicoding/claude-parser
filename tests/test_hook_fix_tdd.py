#!/usr/bin/env python3
"""
TDD: Hook Fix Validation - 100% framework delegation
Uses existing discovery + conversation filtering for real tool data
"""

def test_hook_output_no_exit_with_real_tools():
    """TDD: hook_output should not call sys.exit - real behavior test"""
    from claude_parser import load_latest_session  
    from claude_parser.hooks import hook_output
    
    # Use existing interface to get real tool data
    session = load_latest_session()
    tool_events = [e for e in session.raw_data if e.get('toolUseResult')]
    
    # Real test - if sys.exit() is called, this would terminate the test
    hook_output(reason=f"Validated {len(tool_events)} tools")
    # If we reach this line, sys.exit() was not called - test passes
    assert True