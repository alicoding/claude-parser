"""Tests for pydantic models."""

import pytest
from claude_parser.models import (
    MessageType, BaseMessage, UserMessage, AssistantMessage,
    ToolUse, ToolResult, Summary, SystemMessage, parse_message
)


class TestMessageTypes:
    """Test message type enum."""
    
    def test_message_types(self):
        """Test all message types are defined."""
        assert MessageType.USER == "user"
        assert MessageType.ASSISTANT == "assistant"
        assert MessageType.TOOL_USE == "tool_use"
        assert MessageType.TOOL_RESULT == "tool_result"
        assert MessageType.SUMMARY == "summary"
        assert MessageType.SYSTEM == "system"


class TestUserMessage:
    """Test user message model."""
    
    def test_user_message_creation(self):
        """Test creating user message."""
        msg = UserMessage(
            type="user",
            content="Hello Claude",
            uuid="msg-123",
            sessionId="session-456"
        )
        assert msg.type == MessageType.USER
        assert msg.text_content == "Hello Claude"
        assert msg.uuid == "msg-123"
        assert msg.session_id == "session-456"
    
    def test_user_message_with_structured_content(self):
        """Test user message with structured content."""
        msg = UserMessage(
            type="user",
            message={
                "content": [
                    {"type": "text", "text": "First part"},
                    {"type": "text", "text": "Second part"}
                ]
            }
        )
        assert msg.text_content == "First part\nSecond part"


class TestAssistantMessage:
    """Test assistant message model."""
    
    def test_assistant_message_creation(self):
        """Test creating assistant message."""
        msg = AssistantMessage(
            type="assistant",
            content="Hello! How can I help?",
            uuid="msg-124"
        )
        assert msg.type == MessageType.ASSISTANT
        assert msg.text_content == "Hello! How can I help?"
    
    def test_assistant_message_immutable(self):
        """Test messages are immutable."""
        msg = AssistantMessage(type="assistant", content="Test")
        with pytest.raises(Exception):  # pydantic v2 raises validation error
            msg.content = "Changed"


class TestToolUse:
    """Test tool use model."""
    
    def test_tool_use_creation(self):
        """Test creating tool use message."""
        tool = ToolUse(
            type="tool_use",
            toolUseID="tool-789",
            name="Edit",
            parameters={"file_path": "/src/main.py"}
        )
        assert tool.type == MessageType.TOOL_USE
        assert tool.tool_use_id == "tool-789"
        assert tool.tool_name == "Edit"
        assert tool.parameters["file_path"] == "/src/main.py"


class TestToolResult:
    """Test tool result model."""
    
    def test_tool_result_creation(self):
        """Test creating tool result."""
        result = ToolResult(
            type="tool_result",
            toolUseID="tool-789",
            toolUseResult="File edited successfully"
        )
        assert result.type == MessageType.TOOL_RESULT
        assert result.tool_use_id == "tool-789"
        assert result.result_text == "File edited successfully"


class TestSummary:
    """Test summary model."""
    
    def test_summary_creation(self):
        """Test creating summary."""
        summary = Summary(
            type="summary",
            summary="Discussion about Python refactoring",
            leafUuid="leaf-abc-123"
        )
        assert summary.type == MessageType.SUMMARY
        assert summary.text_content == "Discussion about Python refactoring"
        assert summary.leaf_uuid == "leaf-abc-123"


class TestSystemMessage:
    """Test system message model."""
    
    def test_system_message_creation(self):
        """Test creating system message."""
        msg = SystemMessage(
            type="system",
            content="System notification"
        )
        assert msg.type == MessageType.SYSTEM
        assert msg.text_content == "System notification"


class TestParseMessage:
    """Test message parsing function."""
    
    def test_parse_user_message(self):
        """Test parsing user message."""
        data = {"type": "user", "content": "Hello"}
        msg = parse_message(data)
        assert isinstance(msg, UserMessage)
        assert msg.text_content == "Hello"
    
    def test_parse_assistant_message(self):
        """Test parsing assistant message."""
        data = {"type": "assistant", "content": "Hi there"}
        msg = parse_message(data)
        assert isinstance(msg, AssistantMessage)
    
    def test_parse_tool_use(self):
        """Test parsing tool use."""
        data = {
            "type": "tool_use",
            "toolUseID": "123",
            "name": "Edit"
        }
        msg = parse_message(data)
        assert isinstance(msg, ToolUse)
    
    def test_parse_summary(self):
        """Test parsing summary."""
        data = {
            "type": "summary",
            "summary": "Chat summary",
            "leafUuid": "abc"
        }
        msg = parse_message(data)
        assert isinstance(msg, Summary)
    
    def test_parse_invalid_message(self):
        """Test parsing invalid message returns None."""
        data = {"invalid": "data"}
        msg = parse_message(data)
        # Should return BaseMessage or None for invalid
        assert msg is None or isinstance(msg, BaseMessage)