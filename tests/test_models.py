"""
Comprehensive Pydantic model tests following best practices.

Tests all validation logic, edge cases, and field constraints.
Follows 95/5 principle - uses pytest extensively, minimal custom test code.
"""

import pytest
from pydantic import ValidationError

from claude_parser.models import (
    AssistantMessage,
    BaseMessage,
    MessageType,
    Summary,
    SystemMessage,
    ToolResultContent,
    ToolUseContent,
    UsageInfo,
    UserMessage,
    parse_message,
)
from claude_parser.models.content import TextContent


class TestMessageType:
    """Test MessageType enum validation."""

    def test_valid_message_types(self):
        """Test all valid message types."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.SYSTEM == "system"
        assert MessageType.SUMMARY == "summary"
        assert MessageType.TOOL_USE == "tool_use"
        assert MessageType.TOOL_RESULT == "tool_result"

    def test_message_type_from_string(self):
        """Test creating MessageType from string."""
        assert MessageType("user") == MessageType.USER
        assert MessageType("assistant") == MessageType.ASSISTANT

    def test_invalid_message_type(self):
        """Test invalid message type raises error."""
        with pytest.raises(ValueError):
            MessageType("invalid_type")


class TestBaseMessage:
    """Test BaseMessage validation."""

    def test_minimal_valid_message(self):
        """Test creating minimal valid message."""
        msg = BaseMessage(
            type=MessageType.USER, uuid="test-uuid-123", session_id="test-session"
        )
        assert msg.type == MessageType.USER
        assert msg.uuid == "test-uuid-123"
        assert msg.session_id == "test-session"

    def test_required_fields(self):
        """Test required field validation."""
        # Missing type
        with pytest.raises(ValidationError) as exc_info:
            BaseMessage(uuid="test", session_id="test")
        assert "type" in str(exc_info.value)

        # Missing uuid
        with pytest.raises(ValidationError) as exc_info:
            BaseMessage(type=MessageType.USER, session_id="test")
        assert "uuid" in str(exc_info.value)

    def test_optional_fields(self):
        """Test optional field handling."""
        msg = BaseMessage(
            type=MessageType.USER,
            uuid="test-uuid",
            session_id="test-session",
            parent_uuid="parent-123",
            timestamp="2025-08-25T10:00:00Z",
        )
        assert msg.parent_uuid == "parent-123"
        assert msg.timestamp == "2025-08-25T10:00:00Z"

    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        msg = BaseMessage(
            type=MessageType.USER,
            uuid="test-uuid",
            session_id="test-session",
            extra_field="extra_value",
        )
        assert hasattr(msg, "extra_field")
        assert msg.extra_field == "extra_value"

    def test_string_whitespace_stripped(self):
        """Test string whitespace stripping."""
        msg = BaseMessage(
            type=MessageType.USER, uuid="  test-uuid  ", session_id="  test-session  "
        )
        assert msg.uuid == "test-uuid"
        assert msg.session_id == "test-session"

    def test_text_content_property(self):
        """Test text_content property default."""
        msg = BaseMessage(
            type=MessageType.USER, uuid="test-uuid", session_id="test-session"
        )
        assert msg.text_content == ""


class TestUserMessage:
    """Test UserMessage validation."""

    def test_valid_user_message(self):
        """Test creating valid user message."""
        msg = UserMessage(
            type=MessageType.USER,
            uuid="user-123",
            session_id="session-123",
            message={"content": "Hello world"},
        )
        assert msg.type == MessageType.USER
        assert msg.message == {"content": "Hello world"}
        assert msg.text_content == "Hello world"

    def test_user_message_with_complex_content(self):
        """Test user message with complex content structure."""
        content = [{"type": "text", "text": "Hello"}, {"type": "text", "text": "World"}]
        msg = UserMessage(
            type=MessageType.USER,
            uuid="user-123",
            session_id="session-123",
            message={"content": content},
        )
        assert "Hello" in msg.text_content
        assert "World" in msg.text_content

    def test_user_message_missing_message_field(self):
        """Test user message without message field."""
        msg = UserMessage(
            type=MessageType.USER, uuid="user-123", session_id="session-123"
        )
        assert msg.text_content == ""


class TestAssistantMessage:
    """Test AssistantMessage validation."""

    def test_valid_assistant_message(self):
        """Test creating valid assistant message."""
        msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            uuid="assistant-123",
            session_id="session-123",
            message={"content": [{"type": "text", "text": "Hi there!"}]},
        )
        assert msg.type == MessageType.ASSISTANT
        assert msg.text_content == "Hi there!"

    def test_assistant_with_usage_info(self):
        """Test assistant message with usage information."""
        usage_data = {
            "input_tokens": 100,
            "output_tokens": 50,
            "cache_read_input_tokens": 20,
            "cache_creation_input_tokens": 10,
        }
        msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            uuid="assistant-123",
            session_id="session-123",
            message={
                "content": [{"type": "text", "text": "Response"}],
                "usage": usage_data,
            },
        )
        assert msg.real_usage_info == usage_data
        assert msg.total_tokens == 180  # Sum of all token types

    def test_assistant_tool_uses(self):
        """Test assistant message with tool uses."""
        content = [
            {"type": "text", "text": "Let me search for that."},
            {"type": "tool_use", "name": "search", "input": {"query": "test"}},
        ]
        msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            uuid="assistant-123",
            session_id="session-123",
            message={"content": content},
        )
        tool_uses = msg.tool_uses
        assert len(tool_uses) == 1
        assert tool_uses[0]["name"] == "search"


class TestToolContent:
    """Test tool-related content blocks."""

    def test_tool_use_content(self):
        """Test tool use content block."""
        tool_content = ToolUseContent(
            type="tool_use", id="tool-123", name="search", input={"query": "test"}
        )
        assert tool_content.type == "tool_use"
        assert tool_content.id == "tool-123"
        assert tool_content.name == "search"
        assert tool_content.input == {"query": "test"}

    def test_tool_result_content(self):
        """Test tool result content block."""
        result_content = ToolResultContent(
            type="tool_result", tool_use_id="tool-123", content="Search results here"
        )
        assert result_content.type == "tool_result"
        assert result_content.tool_use_id == "tool-123"
        assert result_content.content == "Search results here"


class TestSummary:
    """Test Summary message validation."""

    def test_valid_summary(self):
        """Test creating valid summary."""
        msg = Summary(
            type=MessageType.SUMMARY,
            uuid="summary-123",
            session_id="session-123",
            summary="This is a conversation summary",
        )
        assert msg.type == MessageType.SUMMARY
        assert msg.summary == "This is a conversation summary"
        assert msg.text_content == "Summary: This is a conversation summary"

    def test_summary_missing_summary_field(self):
        """Test summary without summary field."""
        with pytest.raises(ValidationError) as exc_info:
            Summary(
                type=MessageType.SUMMARY, uuid="summary-123", session_id="session-123"
            )
        assert "summary" in str(exc_info.value)


class TestSystemMessage:
    """Test SystemMessage validation."""

    def test_valid_system_message(self):
        """Test creating valid system message."""
        msg = SystemMessage(
            type=MessageType.SYSTEM,
            uuid="system-123",
            session_id="session-123",
            content="System notification",
        )
        assert msg.type == MessageType.SYSTEM
        assert msg.text_content == "System: System notification"


class TestUsageInfo:
    """Test UsageInfo model validation."""

    def test_valid_usage_info(self):
        """Test creating valid usage info."""
        usage = UsageInfo(
            input_tokens=100,
            output_tokens=50,
            cache_read_input_tokens=20,
            cache_creation_input_tokens=10,
        )
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50
        assert usage.total_tokens == 180

    def test_usage_info_defaults(self):
        """Test usage info with default values."""
        usage = UsageInfo(input_tokens=100, output_tokens=50)
        assert usage.cache_read_input_tokens == 0
        assert usage.cache_creation_input_tokens == 0
        assert usage.total_tokens == 150

    def test_usage_info_negative_values(self):
        """Test usage info rejects negative values."""
        with pytest.raises(ValidationError):
            UsageInfo(input_tokens=-10, output_tokens=50)


class TestContentBlock:
    """Test ContentBlock model validation."""

    def test_text_content_block(self):
        """Test text content block."""
        block = TextContent(type="text", text="Hello world")
        assert block.type == "text"
        assert block.text == "Hello world"


class TestParseMessage:
    """Test parse_message function."""

    def test_parse_user_message(self):
        """Test parsing user message."""
        data = {
            "type": "user",
            "uuid": "user-123",
            "sessionId": "session-123",
            "message": {"content": "Hello"},
        }
        msg = parse_message(data)
        assert isinstance(msg, UserMessage)
        assert msg.type == MessageType.USER

    def test_parse_assistant_message(self):
        """Test parsing assistant message."""
        data = {
            "type": "assistant",
            "uuid": "assistant-123",
            "sessionId": "session-123",
            "message": {"content": [{"type": "text", "text": "Hi"}]},
        }
        msg = parse_message(data)
        assert isinstance(msg, AssistantMessage)
        assert msg.type == MessageType.ASSISTANT

    def test_parse_summary_message(self):
        """Test parsing summary message."""
        data = {
            "type": "summary",
            "uuid": "summary-123",
            "sessionId": "session-123",
            "summary": "Conversation summary",
        }
        msg = parse_message(data)
        assert isinstance(msg, Summary)
        assert msg.type == MessageType.SUMMARY

    def test_parse_system_message(self):
        """Test parsing system message."""
        data = {
            "type": "system",
            "uuid": "system-123",
            "sessionId": "session-123",
            "message": {"content": "System notification"},
        }
        msg = parse_message(data)
        assert isinstance(msg, SystemMessage)
        assert msg.type == MessageType.SYSTEM

    def test_parse_invalid_message_type(self):
        """Test parsing invalid message type returns None."""
        data = {"type": "unknown", "uuid": "unknown-123", "session_id": "session-123"}
        # Invalid message type returns None gracefully
        msg = parse_message(data)
        assert msg is None

    def test_parse_malformed_data(self):
        """Test parsing malformed data."""
        # Missing required fields returns None gracefully
        result = parse_message({"invalid": "data"})
        assert result is None

    def test_parse_empty_data(self):
        """Test parsing empty data."""
        # Empty data returns None gracefully
        result = parse_message({})
        assert result is None

    def test_parse_none_data(self):
        """Test parsing None data."""
        # None data returns None gracefully (parser catches all exceptions)
        result = parse_message(None)
        assert result is None


class TestModelIntegration:
    """Test model integration scenarios."""

    def test_real_claude_message_structure(self):
        """Test parsing real Claude message structure."""
        real_data = {
            "type": "assistant",
            "uuid": "real-uuid-123",
            "sessionId": "real-session-456",
            "timestamp": "2025-08-25T10:00:00.000Z",
            "message": {
                "content": [{"type": "text", "text": "I'll help you with that task."}],
                "usage": {
                    "input_tokens": 150,
                    "output_tokens": 25,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            },
        }

        msg = parse_message(real_data)
        assert isinstance(msg, AssistantMessage)
        assert msg.text_content == "I'll help you with that task."
        assert msg.total_tokens == 175

    def test_conversation_with_mixed_messages(self):
        """Test parsing multiple message types."""
        messages_data = [
            {
                "type": "user",
                "uuid": "u1",
                "sessionId": "s1",
                "message": {"content": "Hello"},
            },
            {
                "type": "assistant",
                "uuid": "a1",
                "sessionId": "s1",
                "message": {"content": [{"type": "text", "text": "Hi there!"}]},
            },
            {
                "type": "summary",
                "uuid": "sum1",
                "sessionId": "s1",
                "summary": "Greeting exchange",
            },
        ]

        messages = [parse_message(data) for data in messages_data]
        assert len(messages) == 3
        assert isinstance(messages[0], UserMessage)
        assert isinstance(messages[1], AssistantMessage)
        assert isinstance(messages[2], Summary)

    def test_model_serialization(self):
        """Test model can be serialized back to dict."""
        msg = UserMessage(
            type=MessageType.USER,
            uuid="user-123",
            session_id="session-123",
            message={"content": "Test message"},
        )

        # Test model_dump works
        data = msg.model_dump()
        assert data["type"] == "user"
        assert data["uuid"] == "user-123"
        assert data["message"]["content"] == "Test message"

    def test_model_json_serialization(self):
        """Test model can be serialized to JSON."""
        msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            uuid="assistant-123",
            session_id="session-123",
            message={"content": [{"type": "text", "text": "Response"}]},
        )

        # Test model_dump_json works
        json_str = msg.model_dump_json()
        assert isinstance(json_str, str)
        assert "assistant" in json_str
        assert "Response" in json_str


# Edge cases and boundary testing
class TestModelEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_long_strings(self):
        """Test handling very long strings."""
        long_text = "x" * 10000
        msg = UserMessage(
            type=MessageType.USER,
            uuid="long-uuid",
            session_id="long-session",
            message={"content": long_text},
        )
        assert len(msg.text_content) == 10000

    def test_unicode_content(self):
        """Test handling unicode content."""
        unicode_text = "Hello 🌍 世界 🚀"
        msg = UserMessage(
            type=MessageType.USER,
            uuid="unicode-uuid",
            session_id="unicode-session",
            message={"content": unicode_text},
        )
        assert msg.text_content == unicode_text

    def test_nested_content_structures(self):
        """Test deeply nested content structures."""
        nested_content = {
            "content": [
                {"type": "text", "text": "Level 1"},
                {
                    "type": "tool_use",
                    "name": "complex_tool",
                    "input": {"nested": {"deeply": {"value": "Level 4"}}},
                },
            ]
        }

        msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            uuid="nested-uuid",
            session_id="nested-session",
            message=nested_content,
        )

        assert "Level 1" in msg.text_content
        tool_uses = msg.tool_uses
        assert len(tool_uses) == 1
        assert tool_uses[0]["name"] == "complex_tool"

    def test_empty_message_content(self):
        """Test messages with empty content."""
        msg = UserMessage(
            type=MessageType.USER,
            uuid="empty-uuid",
            session_id="empty-session",
            message={"content": ""},
        )
        assert msg.text_content == ""

    def test_message_with_null_fields(self):
        """Test messages with null/None fields."""
        msg = BaseMessage(
            type=MessageType.USER,
            uuid="null-uuid",
            session_id="null-session",
            parent_uuid=None,
            timestamp=None,
        )
        assert msg.parent_uuid is None
        assert msg.timestamp is None


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
