"""
TDD Real Data Test for Watch Module
Tests with ACTUAL Claude files using discovery domain
"""
import pytest
import threading
import time
from pathlib import Path

from claude_parser.watch import watch
from claude_parser.discovery import discover_claude_files


def test_watch_with_real_claude_files():
    """TDD Real Data: Use actual Claude files from discovery domain"""
    # Use discovery domain to find REAL Claude files (100% real data)
    claude_files = discover_claude_files(str(Path.home()))
    
    if not claude_files:
        pytest.skip("No real Claude files found for testing")
    
    # Pick the most recent real Claude file
    real_file = claude_files[0]
    
    # Test with REAL Claude file 
    assistant_events = []
    sessions_processed = []
    
    def on_assistant_event(msg):
        assistant_events.append(msg)
    
    def on_session_callback(session):
        sessions_processed.append(session)
    
    # Test that watch can process real Claude files
    print(f"Testing with real Claude file: {real_file}")
    
    try:
        # Watch real file in background thread
        def watch_thread():
            watch(str(real_file), on_assistant=on_assistant_event, callback=on_session_callback)
        
        thread = threading.Thread(target=watch_thread, daemon=True)
        thread.start()
        time.sleep(0.5)  # Let it process real file
        
        # Should have processed the real session
        assert len(sessions_processed) > 0, f"No sessions processed from real file: {real_file}"
        
        real_session = sessions_processed[0]
        assert real_session is not None, "Session should not be None"
        assert len(real_session.messages) > 0, "Real session should have messages"
        
        # Check if we have assistant messages in the real file
        assistant_msgs = [msg for msg in real_session.messages if msg.type == 'assistant']
        if assistant_msgs:
            assert len(assistant_events) > 0, f"Should have detected assistant events from real file"
        else:
            print("No assistant messages in this real file - test passed without assistant events")
            
    except Exception as e:
        pytest.fail(f"Failed to process real Claude file: {e}")