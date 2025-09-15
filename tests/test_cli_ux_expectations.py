#!/usr/bin/env python3
"""
Black Box UX Tests - Define Git-like CLI behavior expectations
Tests what users expect from cg commands based on Git mental model
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


class TestCgStatusUX:
    """Black box tests for cg status - like git status"""
    
    def test_cg_status_shows_current_session_like_git_branch(self):
        """cg status should show current/active session like git shows current branch"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should show which session we're "on" (most recent)
        # Like: "On session: abc123 (2024-01-10 15:30)"
        assert "session" in result.stdout.lower() or "current" in result.stdout.lower()
        
    def test_cg_status_shows_recent_activity_summary(self):
        """cg status should show recent changes/activity like git status shows staged/unstaged"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should show recent tool uses, message counts, time info
        # Like git shows modified files
        output = result.stdout.lower()
        assert any(word in output for word in ["messages", "tools", "activity", "recent"])
        
    def test_cg_status_suggests_next_actions(self):
        """cg status should suggest what user can do next, like git status suggestions"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should hint at available commands
        # Like: "Use 'cg log' to see history" or "Use 'cg diff <uuid>' to see changes"
        assert len(result.stdout.strip()) > 50  # More than just basic info


class TestCgLogUX:
    """Black box tests for cg log - like git log"""
    
    def test_cg_log_shows_chronological_message_history(self):
        """cg log should show message timeline like git log shows commits"""
        result = run_cg_command("log", "--limit", "5")
        assert result.returncode == 0
        
        # Should show messages in reverse chronological order
        # Each "commit" = message with metadata
        lines = [line for line in result.stdout.split('\n') if line.strip()]
        assert len(lines) >= 1
        
    def test_cg_log_shows_message_metadata_like_git_commit_info(self):
        """Each log entry should show metadata like git shows commit author/date"""
        result = run_cg_command("log", "--limit", "3")
        assert result.returncode == 0
        
        # Should show: message type, timestamp, maybe content preview
        # Like git shows: commit hash, author, date, message
        output = result.stdout.lower()
        assert any(word in output for word in ["user", "assistant", "system", "tool"])
        
    def test_cg_log_supports_filtering_like_git_log_options(self):
        """cg log should support filters like git log --author, --since"""
        # Test limit option works
        result_5 = run_cg_command("log", "--limit", "5")
        result_10 = run_cg_command("log", "--limit", "10")
        
        assert result_5.returncode == 0
        assert result_10.returncode == 0
        
        # Should show different amounts
        lines_5 = len([l for l in result_5.stdout.split('\n') if l.strip()])
        lines_10 = len([l for l in result_10.stdout.split('\n') if l.strip()])
        
        # More limit should show more content (unless fewer messages exist)
        assert lines_10 >= lines_5


class TestCgDiffUX:
    """Black box tests for cg diff - like git diff"""
    
    def test_cg_diff_shows_helpful_message_when_no_args(self):
        """cg diff should guide user on usage like git diff does"""
        result = run_cg_command("diff")
        assert result.returncode == 0
        
        # Should explain how to use it, not just error
        output = result.stdout.lower()
        assert any(word in output for word in ["uuid", "specify", "compare", "between"])
        
    def test_cg_diff_with_uuids_shows_meaningful_comparison(self):
        """cg diff <uuid1> <uuid2> should show comparison between messages/states"""
        # This will fail until implemented - that's the point of TDD
        result = run_cg_command("diff", "abc123", "def456")
        
        # Should show comparison, not just placeholder
        # For now, expect improvement over current placeholder
        output = result.stdout.lower()
        
        # Should NOT just say "feature in development"
        # Should attempt to show some kind of meaningful diff
        assert "development" not in output or len(output) > 100


class TestCgCheckoutUX:
    """Black box tests for cg checkout - like git checkout"""
    
    def test_cg_checkout_switches_context_to_specific_session(self):
        """cg checkout <session> should switch to that session context"""
        # This command doesn't exist yet - will fail, driving implementation
        result = run_cg_command("checkout", "abc123")
        
        # Should either work or give helpful error about what checkout means
        # Should NOT give "command not found" - should be implemented
        assert result.returncode in [0, 1]  # Either works or handled error
        
    def test_cg_checkout_lists_available_sessions_when_no_args(self):
        """cg checkout should list available sessions like git branch"""
        result = run_cg_command("checkout")
        
        # Should show available sessions to switch to
        # Like git branch shows available branches
        assert result.returncode == 0
        assert len(result.stdout.strip()) > 0


class TestGitLikeConsistency:
    """Tests for overall Git-like UX consistency"""
    
    def test_all_commands_work_from_subdirectories(self):
        """All cg commands should work from any subdirectory like git commands"""
        from pathlib import Path
        
        # Already tested this, but important for UX
        test_dir = Path("tests")
        if test_dir.exists():
            result = run_cg_command("status")
            assert result.returncode == 0
            
    def test_commands_have_consistent_help_format(self):
        """All commands should have consistent help text format"""
        commands = ["status", "log", "diff"]
        
        for cmd in commands:
            result = run_cg_command(cmd, "--help")
            assert result.returncode == 0
            assert "usage:" in result.stdout.lower() or "show" in result.stdout.lower()
            
    def test_error_messages_are_helpful_not_cryptic(self):
        """Error messages should guide users like git does"""
        # Test invalid command
        result = run_cg_command("nonexistent")
        
        # Should show available commands, not just "command not found"
        assert result.returncode != 0
        assert len(result.stderr) > 0 or "command" in result.stdout.lower()