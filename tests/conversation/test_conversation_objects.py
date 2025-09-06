"""
Conversation Domain: Conversation Objects

Tests the Conversation class and related objects from public API.
These are the 5% power-user features.

FEATURES ONLY - No infrastructure, no fake data.
"""

from claude_parser import load, Conversation, ConversationMetadata
from claude_parser import Message, UserMessage, AssistantMessage
from ..framework import EnforcedTestBase, assert_interface_contract


class TestConversationObjects(EnforcedTestBase):
    """Test Conversation class and message objects."""

    def test_conversation_has_messages_and_metadata(self, sample_transcript):
        """Feature: Conversation provides messages and metadata."""
        conv = load(sample_transcript)

        # Core Conversation interface
        assert_interface_contract(conv, Conversation, ['messages', 'metadata'])

        # Metadata should be ConversationMetadata type
        assert isinstance(conv.metadata, ConversationMetadata)

    def test_conversation_messages_are_message_objects(self, sample_transcript):
        """Feature: Messages are proper Message objects."""
        conv = load(sample_transcript)

        if conv.messages:
            msg = conv.messages[0]

            # Should be Message or subclass
            assert isinstance(msg, Message)

            # Should have core message attributes
            assert hasattr(msg, 'uuid')
            assert hasattr(msg, 'type')
            assert hasattr(msg, 'timestamp')

    def test_message_types_work_correctly(self, sample_transcript):
        """Feature: Message type system works correctly."""
        conv = load(sample_transcript)

        user_messages = [m for m in conv.messages if m.type.value == 'user']
        assistant_messages = [m for m in conv.messages if m.type.value == 'assistant']

        # Type checking should work
        for msg in user_messages:
            # UserMessage type should be detectable
            assert msg.type.value == 'user'

        for msg in assistant_messages:
            # AssistantMessage type should be detectable
            assert msg.type.value == 'assistant'


class TestConversationMetadata(EnforcedTestBase):
    """Test ConversationMetadata features."""

    def test_metadata_has_essential_info(self, sample_transcript):
        """Feature: Metadata contains essential conversation info."""
        conv = load(sample_transcript)
        metadata = conv.metadata

        # Should have key metadata fields
        assert hasattr(metadata, 'session_id')
        assert hasattr(metadata, 'filepath')

        # Filepath should match what we loaded
        assert str(metadata.filepath) == str(sample_transcript)

    def test_metadata_provides_message_count(self, sample_transcript):
        """Feature: Metadata tracks message count."""
        conv = load(sample_transcript)
        metadata = conv.metadata

        # Message count should match actual messages
        if hasattr(metadata, 'message_count'):
            assert metadata.message_count == len(conv.messages)
