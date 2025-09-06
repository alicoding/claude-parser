"""TDD Tests for Conversation alias methods.

These tests ensure backward compatibility when consolidating Conversation classes.
"""

import pytest
from pathlib import Path
from claude_parser import load
from claude_parser.domain.entities.conversation import Conversation
from claude_parser.domain.value_objects.metadata import ConversationMetadata
from claude_parser.models import (
    MessageType, UserMessage, AssistantMessage, ToolUse, ToolResult, Summary
)


@pytest.fixture
def sample_conversation():
    """Create a sample conversation with various message types."""
    messages = [
        UserMessage(type=MessageType.USER, content="Hello"),
        AssistantMessage(type=MessageType.ASSISTANT, content="Hi there!"),
        ToolUse(type=MessageType.TOOL_USE, tool_use_id="tool-1", name="Read", parameters={"file": "test.py"}),
        ToolResult(type=MessageType.TOOL_RESULT, tool_use_id="tool-1", output="file contents"),
        UserMessage(type=MessageType.USER, content="Show error"),
        AssistantMessage(type=MessageType.ASSISTANT, content="Here's an error message"),
        Summary(type=MessageType.SUMMARY, summary="Conversation summary"),
        UserMessage(type=MessageType.USER, content="After summary"),
    ]

    metadata = ConversationMetadata(
        filepath=Path("test.jsonl"),
        session_id="test-session",
        current_dir="/test/dir",
        git_branch="main",
        message_count=len(messages),
        error_count=1  # One message contains "error"
    )

    return Conversation(messages=messages, metadata=metadata)


class TestConversationAliases:
    """Test alias methods for backward compatibility."""

    def test_tool_messages_alias(self, sample_conversation):
        """Test that tool_messages() is an alias for tool_uses property."""
        # Both should return the same tool-related messages
        tool_uses = sample_conversation.tool_uses
        tool_messages = sample_conversation.tool_messages()

        assert tool_messages == tool_uses
        assert len(tool_messages) == 2  # ToolUse and ToolResult
        assert any(isinstance(m, ToolUse) for m in tool_messages)
        assert any(isinstance(m, ToolResult) for m in tool_messages)

    def test_messages_with_errors_alias(self, sample_conversation):
        """Test that messages_with_errors() is an alias for with_errors()."""
        # Both should return messages containing "error"
        with_errors = sample_conversation.with_errors()
        messages_with_errors = sample_conversation.messages_with_errors()

        assert messages_with_errors == with_errors
        assert len(messages_with_errors) == 2  # Both "Show error" and "Here's an error message"
        assert all("error" in msg.text_content.lower() for msg in messages_with_errors)

    def test_messages_before_summary_alias(self, sample_conversation):
        """Test that messages_before_summary() is an alias for before_summary()."""
        # Both should return messages before the summary
        before_summary = sample_conversation.before_summary(limit=5)
        messages_before_summary = sample_conversation.messages_before_summary(limit=5)

        assert messages_before_summary == before_summary
        # Should have messages before the Summary message
        assert all(not isinstance(m, Summary) for m in messages_before_summary)
        assert len(messages_before_summary) <= 5

    def test_all_original_methods_still_work(self, sample_conversation):
        """Ensure all original methods continue to work."""
        # Properties should work
        assert sample_conversation.messages is not None
        assert sample_conversation.assistant_messages is not None
        assert sample_conversation.user_messages is not None
        assert sample_conversation.tool_uses is not None
        assert sample_conversation.summaries is not None

        # Methods should work
        assert sample_conversation.search("Hello") is not None
        assert sample_conversation.filter(lambda m: True) is not None
        assert sample_conversation.with_errors() is not None
        assert sample_conversation.before_summary() is not None
