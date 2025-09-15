#!/usr/bin/env python3
"""
Discovery Interface Tests - LNCA_TEST_PATTERN
Interface Testing + Contract Testing + Integration Testing + BDD + Real Data + Black Box
"""

import pytest
from pathlib import Path
from claude_parser import discover_claude_files, group_by_projects, analyze_project_structure


def test_discover_claude_files_interface_contract():
    """Interface Test: discover_claude_files accepts string path and returns List[Path]"""
    # Contract: function should exist and accept string
    result = discover_claude_files(".")
    
    # Contract: should return list of Path objects
    assert isinstance(result, list)
    assert all(isinstance(f, Path) for f in result)


def test_discover_claude_files_with_real_project_data():
    """Integration Test: discover_claude_files finds real Claude files"""
    # Real Data: Use current project directory
    current_dir = "/Volumes/AliDev/ai-projects/claude-parser"
    result = discover_claude_files(current_dir)
    
    # BDD: Should find JSONL files if they exist in the project
    jsonl_files = [f for f in result if f.suffix == '.jsonl']
    
    # Contract: Real project may or may not have Claude files
    assert isinstance(result, list)
    # Integration: If files found, they should be valid paths
    for file in result:
        assert file.exists()


def test_group_by_projects_contract():
    """Contract Test: group_by_projects processes real discovered files"""
    files = discover_claude_files("/Volumes/AliDev/ai-projects/claude-parser")
    result = group_by_projects(files)
    
    # Contract: should return dict with Path keys and List[Path] values
    assert isinstance(result, dict)
    for project_path, project_files in result.items():
        assert isinstance(project_path, Path)
        assert isinstance(project_files, list)
        assert all(isinstance(f, Path) for f in project_files)


def test_analyze_project_structure_interface_real_data():
    """Interface Test: analyze_project_structure works with real project path"""
    current_project = Path("/Volumes/AliDev/ai-projects/claude-parser")
    result = analyze_project_structure(current_project)
    
    # Contract: should return dict with known keys
    assert isinstance(result, dict)
    if result:  # If project exists
        assert 'path' in result
        assert 'total_files' in result
        assert 'file_types' in result
        assert 'has_git' in result
        
        # BDD: Real project should have Python files
        assert isinstance(result['is_python'], bool)


def test_invalid_path_handling_contract():
    """Contract Test: Functions handle invalid paths gracefully"""
    # BDD: Non-existent path should not crash
    result = discover_claude_files("/nonexistent/path")
    assert result == []
    
    result = analyze_project_structure(Path("/nonexistent/path"))
    assert result == {}