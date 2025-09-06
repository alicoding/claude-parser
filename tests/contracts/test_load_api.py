"""
Test load() API feature - Interface contract only.

Tests FEATURES:
- Can I load a conversation from a file?
- Does load() return what I expect?
- Does it handle edge cases gracefully?

NO infrastructure testing, NO framework internals, NO fake data.
"""

from claude_parser import load, Conversation
from ..framework import EnforcedTestBase, assert_interface_contract


class TestLoadAPIFeature(EnforcedTestBase):
    """Test load() feature through public API interface."""

    def test_load_returns_conversation_object(self, sample_transcript):
        """Feature: load() returns a Conversation object."""
        # Test the feature - can I load a conversation?
        conv = load(sample_transcript)

        # Verify the interface contract
        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])

    def test_load_conversation_has_messages(self, sample_transcript):
        """Feature: Loaded conversation contains messages."""
        conv = load(sample_transcript)

        # Feature test: Does the conversation have messages?
        assert len(conv.messages) > 0
        assert all(hasattr(msg, 'uuid') for msg in conv.messages)

    def test_load_handles_empty_file(self, empty_jsonl_file):
        """Feature: load() handles empty files gracefully."""
        conv = load(empty_jsonl_file)

        # Feature test: Empty file = empty conversation
        assert isinstance(conv, Conversation)
        assert len(conv.messages) == 0
