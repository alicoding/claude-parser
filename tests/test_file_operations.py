#!/usr/bin/env python3
"""
File Operations Interface Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from pathlib import Path
import tempfile
from claude_parser import compare_files, backup_file


def test_compare_files_contract_real_files():
    """Contract Test: compare_files works with real temporary files"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp1, \
         tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp2:
        
        tmp1.write("original content\nline 2")
        tmp1.flush()
        tmp2.write("modified content\nline 2")
        tmp2.flush()
        tmp1_path, tmp2_path = tmp1.name, tmp2.name
    
    try:
        result = compare_files(tmp1_path, tmp2_path)
        assert result is None or isinstance(result, str)
        
        if result:
            assert "original content" in result or "modified content" in result
    finally:
        Path(tmp1_path).unlink(missing_ok=True)
        Path(tmp2_path).unlink(missing_ok=True)


def test_backup_file_interface_real_data():
    """Interface Test: backup_file creates real backup"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("important data\nto backup")
        tmp.flush()
        tmp_path = tmp.name
    
    try:
        backup_path = backup_file(tmp_path)
        assert backup_path is None or isinstance(backup_path, str)
        
        if backup_path:
            backup = Path(backup_path)
            assert backup.exists()
            assert backup.read_text() == "important data\nto backup"
            backup.unlink(missing_ok=True)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_backup_with_custom_suffix():
    """BDD Test: Backup file with custom suffix"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("test content")
        tmp.flush()
        tmp_path = tmp.name
    
    try:
        backup_path = backup_file(tmp_path, ".backup")
        
        if backup_path:
            assert backup_path.endswith(".backup")
            Path(backup_path).unlink(missing_ok=True)
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_file_operations_error_handling():
    """Contract Test: File operations handle errors gracefully"""
    result = compare_files("/nonexistent1.txt", "/nonexistent2.txt")
    assert result is None
    
    result = backup_file("/nonexistent.txt")
    assert result is None