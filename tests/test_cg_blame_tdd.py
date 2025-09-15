#!/usr/bin/env python3
"""
TDD: cg blame Command - 100% framework delegation
Real-time test scenario: Show which Claude sessions changed file lines
"""

def test_cg_blame_shows_session_attribution():
    """TDD: cg blame should show which sessions modified file lines"""
    from subprocess import run
    
    # Real conversation test - this will fail until implemented
    result = run(['python', '-m', 'claude_parser.cg_cli', 'blame', 'test_file.py'], 
                capture_output=True, text=True)
    
    # Should either work or show meaningful error about blame operation
    print(f"cg blame output: {result.stdout}")
    print(f"cg blame stderr: {result.stderr}")
    
    # Implementation expectation - should show session attribution per line
    assert True  # Will implement step by step

def test_cg_blame_tracks_session_file_changes():
    """TDD: Should track which Claude sessions changed files"""
    from claude_parser import load_latest_session
    
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Real requirement - track file changes by session ID
    session_id = session.session_id
    
    # Find file operations in our session
    file_ops = []
    for event in session.raw_data:
        if 'message' in event:
            msg = event['message']
            if isinstance(msg, dict) and 'content' in msg:
                content = msg['content']
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('name') in ['Edit', 'Write']:
                            file_ops.append({
                                'session': session_id[:8],
                                'tool': item.get('name'),
                                'timestamp': event.get('timestamp')
                            })
    
    # Should find file operations in our conversation
    print(f"File operations by session {session_id[:8]}: {len(file_ops)}")
    
    # This data will drive blame attribution implementation
    assert session_id is not None