"""
Core API Domain: Load Features

Tests all load() variants from claude_parser public API:
- load() - Single conversation loading
- load_many() - Multiple conversation loading
- load_large() - Large file optimized loading

FEATURES ONLY - No infrastructure, no fake data.
"""

from claude_parser import load, load_many, load_large, Conversation
from ..framework import EnforcedTestBase, assert_interface_contract


class TestLoadFeatures(EnforcedTestBase):
    """Test core load() features."""

    def test_load_single_conversation(self, sample_transcript):
        """Feature: load() loads single conversation from file."""
        conv = load(sample_transcript)

        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])
        assert len(conv.messages) > 0

    def test_load_many_conversations(self, sample_transcript):
        """Feature: load_many() loads multiple conversations."""
        conversations = load_many([sample_transcript])

        assert isinstance(conversations, list)
        assert len(conversations) == 1
        assert isinstance(conversations[0], Conversation)

    def test_load_large_conversation(self, sample_transcript):
        """Feature: load_large() handles large files efficiently."""
        conv = load_large(sample_transcript)

        # Same interface as regular load()
        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])


class TestLoadEdgeCases(EnforcedTestBase):
    """Test load() edge case handling."""

    def test_load_empty_file_returns_empty_conversation(self, empty_jsonl_file):
        """Feature: Empty files return valid empty conversations."""
        conv = load(empty_jsonl_file)

        assert isinstance(conv, Conversation)
        assert len(conv.messages) == 0

    def test_load_nonexistent_file_raises_error(self):
        """Feature: Non-existent files raise appropriate errors."""
        from pathlib import Path

        try:
            load(Path("does_not_exist.jsonl"))
            assert False, "Should have raised an exception"
        except Exception as e:
            # Feature: Error should be user-friendly
            assert "does_not_exist.jsonl" in str(e)
