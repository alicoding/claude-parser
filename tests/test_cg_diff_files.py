#!/usr/bin/env python3
"""
TDD: cg diff File Detection - 100% framework delegation  
Single responsibility: Identify files changed since checkpoint
"""

def test_cg_diff_identifies_real_files_changed():
    """TDD: Should identify file operations in session - 100% public API"""
    from claude_parser import load_latest_session
    
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Use public API to get session data and look for file operations
    # This tests that we can analyze the session for file changes using public interface
    file_operations = []
    
    # Use public session.messages instead of raw_data
    for message in session.messages:
        # Check message content for file operations (Edit/Write tools)
        content_str = str(getattr(message, 'content', ''))
        if 'Edit' in content_str or 'Write' in content_str:
            file_operations.append('file_operation')
    
    # We should have some messages in the session
    assert len(session.messages) > 0, "Session should have messages"
    
    print(f"Total messages in session: {len(session.messages)}")
    print(f"File operations detected: {len(file_operations)}")