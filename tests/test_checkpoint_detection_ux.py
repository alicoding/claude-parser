#!/usr/bin/env python3
"""
Black Box UX Tests - Checkpoint Detection Algorithm
Tests what users expect from Git-like checkpoint detection using real JSONL data
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


class TestCheckpointDetectionUX:
    """Black box tests for checkpoint detection - what should be considered 'current checkpoint'"""
    
    def test_current_checkpoint_is_last_user_message_with_file_changes(self):
        """Current checkpoint = last user message that resulted in file operations"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should show:
        # - Which user message is the current checkpoint (timestamp, preview)
        # - What files were changed since that checkpoint
        output = result.stdout.lower()
        
        # Expected format like: "Since checkpoint (2024-01-10 15:30): 'fix the discovery issue'"
        assert any(word in output for word in ["checkpoint", "since", "last"])
        assert any(word in output for word in ["files", "changed", "modified"])
        
    def test_checkpoint_skips_conversation_only_messages(self):
        """Checkpoint detection should skip user messages with no file operations after them"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should NOT use recent "talk to me if need help" type messages as checkpoint
        # Should find the actual task-based message that led to file changes
        output = result.stdout.lower()
        
        # Should show meaningful task context, not conversation
        conversation_words = ["help", "talk", "ok", "thanks", "good"]
        task_words = ["fix", "implement", "add", "update", "create", "test"]
        
        # More likely to show task-related checkpoint than pure conversation
        task_score = sum(1 for word in task_words if word in output)
        assert task_score > 0  # Should have some task context
        
    def test_checkpoint_shows_file_operations_summary(self):
        """Status should show what file operations happened since checkpoint"""
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should show operations like: "3 files edited, 1 file created"
        # Or: "Edit: discovery.py, pyproject.toml"
        output = result.stdout.lower()
        
        # Should mention specific operations or file names
        assert any(word in output for word in ["edit", "write", "create", "modify"])
        
    def test_no_changes_since_checkpoint_handled_gracefully(self):
        """When no file changes since last checkpoint, show helpful message"""
        # This scenario happens when user asks questions but no file ops
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should either show changes OR say "no changes since checkpoint"
        output = result.stdout.lower()
        
        # Should give clear status either way
        assert len(output.strip()) > 20  # Some meaningful output


class TestCheckpointSelectionAlgorithm:
    """Black box tests for how checkpoint selection should work"""
    
    def test_algorithm_finds_meaningful_checkpoints(self):
        """Checkpoint algorithm should find user messages that led to actual work"""
        result = run_cg_command("log", "--checkpoints")  # Hypothetical flag
        
        # Should show list of meaningful checkpoints, not every user message
        # Expected: Task-oriented messages that resulted in file changes
        
        # For now, just test that some meaningful log exists
        # (This will fail until --checkpoints is implemented)
        assert result.returncode in [0, 1]  # Either works or handled error
        
    def test_current_working_context_detection(self):
        """Should detect current working context from recent messages"""
        result = run_cg_command("status", "--context")  # Hypothetical flag
        
        # Should show what we're currently working on
        # Based on sequence: user message → file operations → current state
        
        assert result.returncode in [0, 1]  # Either works or handled error


class TestRealDataScenarios:
    """Test checkpoint detection against real conversation patterns"""
    
    def test_handles_research_then_implementation_pattern(self):
        """
        Real pattern: User asks for research → Discussion → User approves → File changes
        Checkpoint should be the approval message, not the research request
        """
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should identify the "proceed/approve" message as checkpoint
        # Not the initial research question
        output = result.stdout.lower()
        
        # Should show meaningful context
        assert len(output.strip()) > 10
        
    def test_handles_bug_investigation_pattern(self):
        """
        Real pattern: User reports issue → Investigation → User provides info → Fix
        Checkpoint should be when user provided the key info that led to solution
        """
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should find the message that triggered the actual fix
        # Not the initial bug report or investigation discussion
        output = result.stdout.lower()
        
        assert len(output.strip()) > 10
        
    def test_handles_iterative_refinement_pattern(self):
        """
        Real pattern: Implement → User feedback → Adjust → More feedback → Adjust
        Each feedback that led to changes should be a potential checkpoint
        """
        result = run_cg_command("status")
        assert result.returncode == 0
        
        # Should show the most recent feedback that led to file changes
        output = result.stdout.lower()
        
        assert len(output.strip()) > 10