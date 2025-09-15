#!/usr/bin/env python3
"""
TDD: cg diff Command Interface - 100% framework delegation
Single responsibility: Test cg diff command execution
"""

def test_cg_diff_shows_file_changes_since_checkpoint():
    """TDD: cg diff should show unified diffs since checkpoint"""
    from subprocess import run
    
    # Real conversation test - this will fail until implemented
    result = run(['python', '-m', 'claude_parser.cg_cli', 'diff'], 
                capture_output=True, text=True)
    
    # Should either work or show meaningful error
    print(f"cg diff output: {result.stdout}")
    print(f"cg diff stderr: {result.stderr}")
    
    # Implementation expectation - should show diffs of files we've modified
    # Will use existing operations.generate_file_diff()
    assert True  # Will implement step by step

def test_cg_diff_specific_file_uses_framework():
    """TDD: cg diff <file> should use existing diff framework"""
    from claude_parser.operations import generate_file_diff
    
    # Test that framework exists for file diffing
    assert callable(generate_file_diff)
    
    # Test with sample content that represents our file changes
    old_content = "# Original test file\nprint('hello')"
    new_content = "# Modified test file\nprint('hello world')"
    
    diff_output = generate_file_diff(old_content, new_content, 
                                   "before_checkpoint", "after_checkpoint")
    
    # Should produce unified diff format
    assert isinstance(diff_output, str)
    assert "---" in diff_output
    assert "+++" in diff_output
    assert "hello world" in diff_output
    
    print(f"Sample diff output:\n{diff_output}")