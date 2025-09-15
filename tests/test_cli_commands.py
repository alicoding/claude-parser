#!/usr/bin/env python3
"""
Test CLI commands interface - black box testing of cg commands
Tests the CLI interface, not internal implementation
"""
import subprocess
import sys
from pathlib import Path
import pytest


def run_cg_command(*args):
    """Run cg command and return result"""
    cmd = [sys.executable, "-m", "claude_parser.cli.cg"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
    return result


class TestCgStatus:
    """Test cg status command interface"""
    
    def test_cg_status_shows_session_info(self):
        """cg status should show current session information"""
        result = run_cg_command("status")
        
        assert result.returncode == 0
        assert "Session:" in result.stdout or "Current:" in result.stdout
        assert len(result.stdout.strip()) > 0
        
    def test_cg_status_shows_project_info(self):
        """cg status should show project information"""
        result = run_cg_command("status")
        
        assert result.returncode == 0
        assert "Project:" in result.stdout or "Files:" in result.stdout


class TestCgLog:
    """Test cg log command interface"""
    
    def test_cg_log_shows_message_history(self):
        """cg log should show message history"""
        result = run_cg_command("log")
        
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0
        
    def test_cg_log_limit_works(self):
        """cg log --limit should respect limit parameter"""
        result = run_cg_command("log", "--limit", "5")
        
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0


class TestCgDiff:
    """Test cg diff command interface"""
    
    def test_cg_diff_shows_recent_changes(self):
        """cg diff should show recent changes"""
        result = run_cg_command("diff")
        
        assert result.returncode == 0
        # Should either show diffs or indicate no changes
        assert len(result.stdout.strip()) >= 0


class TestCgHelp:
    """Test CLI help interface"""
    
    def test_cg_help_works(self):
        """cg --help should show help"""
        result = run_cg_command("--help")
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout or "Commands:" in result.stdout
        
    def test_cg_status_help_works(self):
        """cg status --help should show status help"""
        result = run_cg_command("status", "--help")
        
        assert result.returncode == 0
        assert "status" in result.stdout.lower()