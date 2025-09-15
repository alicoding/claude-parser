#!/usr/bin/env python3
"""
Hook Interface Tests: Black Box API Testing with Real Data
@API_FIRST_TEST_DATA compliant - uses public execute_hook API only
"""

def test_execute_hook_with_real_session_data():
    """Hook Test: execute_hook processes real session data without errors"""
    from claude_parser import load_latest_session  
    from claude_parser.hooks import execute_hook
    
    # Use public API to get real session data
    session = load_latest_session()
    if not session:
        # If no session, just test basic API functionality
        execute_hook("PreToolUse", tool_name="Read", tool_input='{"file_path": "/test.py"}')
        return
        
    # Use real session data with execute_hook - black box test
    execute_hook(
        hook_event_name="PreToolUse",
        session_id=session.session_id,
        transcript_path="/test/transcript.jsonl",
        cwd="/test/project",
        tool_name="Read",
        tool_input='{"file_path": "/test.py"}'
    )

def test_execute_hook_handles_all_hook_events():
    """Hook Test: execute_hook processes ALL hook event types"""
    from claude_parser import load_latest_session
    from claude_parser.hooks import execute_hook
    
    # Use public API to get session context
    session = load_latest_session()
    session_id = session.session_id if session else "test"
    
    # Test all hook event types with real session data
    hook_types = [
        "PreToolUse", "PostToolUse", "UserPromptSubmit", "Notification",
        "Stop", "SubagentStop", "PreCompact", "SessionStart", "SessionEnd"
    ]
    
    for hook_type in hook_types:
        # Black box test - should not raise exceptions
        execute_hook(
            hook_event_name=hook_type,
            session_id=session_id,
            transcript_path="/test.jsonl",
            cwd="/test"
        )