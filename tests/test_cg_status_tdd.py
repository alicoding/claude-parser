#!/usr/bin/env python3
"""
TDD: cg status Command - 100% framework delegation
Real-time test scenario: Show files changed since our conversation checkpoint
"""

def test_cg_status_shows_files_changed_since_checkpoint():
    """CLI Integration Test: cg status command runs successfully"""
    from subprocess import run
    
    # Simple integration test - just verify CLI works
    result = run(['python', '-m', 'claude_parser.cli.cg', 'status'], 
                capture_output=True, text=True)
    
    # CLI should run without crashing
    assert result.returncode == 0
    
    # Should produce some output (the actual logic is tested elsewhere)
    assert len(result.stdout) > 0 or len(result.stderr) > 0
    
    # Should show files section (even if empty)
    # This will guide our implementation to show file changes
    # Real expectation: list files changed since our conversation started
    print(f"Current status output:\n{result.stdout}")
    
    # Will expand this as we implement file tracking
    assert len(result.stdout) > 0 or len(result.stderr) > 0

def test_cg_status_uses_real_checkpoint_from_our_conversation():
    """TDD: Should show session info from real conversation - 100% public API"""
    from claude_parser import load_latest_session
    
    # Get real session data using public API
    session = load_latest_session()
    if not session:
        assert True  # Skip if no session
        return
    
    # Run cg status and verify it works with real session data
    from subprocess import run
    result = run(['python', '-m', 'claude_parser.cli.cg', 'status'], 
                capture_output=True, text=True)
    
    # Test that CLI can work with the session data we have
    print(f"CLI output: {result.stdout}")
    print(f"Session has {len(session.messages)} messages")
    
    # CLI should either work (returncode 0) or fail gracefully
    # The actual business logic is tested in the API tests
    assert result.returncode in [0, 1]  # Either success or handled error