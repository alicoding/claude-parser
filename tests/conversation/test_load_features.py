"""
Conversation Domain: Load Features

Foundation tests - ALL other domains depend on load() working.
Tests the core 95% use case API from claude_parser public interface.

FEATURES ONLY - No infrastructure, no fake data.
"""

from claude_parser import load, load_many, load_large, Conversation
from ..framework import EnforcedTestBase, assert_interface_contract


class TestLoadFeatures(EnforcedTestBase):
    """Test core load() features that enable all other domains."""

    def test_load_single_conversation(self, sample_transcript):
        """Foundation: load() returns Conversation with messages."""
        conv = load(sample_transcript)

        # Core interface contract
        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])
        assert len(conv.messages) > 0

    def test_load_many_conversations(self, sample_transcript):
        """Feature: load_many() handles multiple transcripts."""
        conversations = load_many([sample_transcript])

        assert isinstance(conversations, list)
        assert len(conversations) == 1
        assert isinstance(conversations[0], Conversation)

    def test_load_large_conversation(self, sample_transcript):
        """Feature: load_large() optimized for large files."""
        conv = load_large(sample_transcript)

        # Same interface as load() - consistency
        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])


class TestLoadEdgeCases(EnforcedTestBase):
    """Edge cases that other domains rely on."""

    def test_empty_file_returns_empty_conversation(self, empty_jsonl_file):
        """Edge case: Empty files = valid empty conversations."""
        conv = load(empty_jsonl_file)

        assert isinstance(conv, Conversation)
        assert len(conv.messages) == 0

    def test_nonexistent_file_raises_clear_error(self):
        """Edge case: Clear error messages for missing files."""
        from pathlib import Path

        try:
            load(Path("nonexistent.jsonl"))
            assert False, "Should raise exception"
        except Exception as e:
            # Error should be user-friendly
            assert "nonexistent.jsonl" in str(e)
