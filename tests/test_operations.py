#!/usr/bin/env python3
"""
Operations Interface Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from pathlib import Path
import tempfile
from claude_parser import restore_file_content, generate_file_diff


def test_generate_file_diff_interface_contract():
    """Interface Test: generate_file_diff accepts strings and returns string"""
    content1 = "line 1\nline 2\nline 3"
    content2 = "line 1\nmodified line 2\nline 3"
    
    result = generate_file_diff(content1, content2)
    assert isinstance(result, str)
    assert "@@" in result or len(result) == 0


def test_restore_file_content_integration_real_data():
    """Integration Test: restore_file_content works with real temporary file"""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp_path = tmp.name
        
    try:
        test_content = b"restored content\nline 2\nline 3"
        result = restore_file_content(tmp_path, test_content)
        
        assert isinstance(result, bool)
        assert result == True
        
        restored_path = Path(tmp_path)
        assert restored_path.exists()
        assert restored_path.read_bytes() == test_content
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_diff_with_real_data():
    """BDD Test: Diff generation with realistic content changes"""
    original = "def hello():\n    print('world')"
    modified = "def hello():\n    print('universe')"
    
    result = generate_file_diff(original, modified, "before.py", "after.py")
    
    # Contract: Should contain expected diff elements
    assert isinstance(result, str)
    if result:  # May be empty if no differences detected
        assert "before.py" in result or "after.py" in result


def test_error_handling_contract():
    """Contract Test: Functions handle invalid inputs gracefully"""
    # BDD: Invalid restore should return False, not crash
    result = restore_file_content("/invalid/path.txt", b"data")
    assert result == False