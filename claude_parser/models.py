"""
Message models - Backward compatibility.

This file maintains backward compatibility.
The actual implementation is in the models/ package.

SOLID: Single import/export responsibility
"""

from .models import (
    AssistantMessage,
    BaseMessage,
    Message,
    MessageType,
    Summary,
    SystemMessage,
    ToolResult,
    ToolUse,
    UserMessage,
    parse_message,
)

__all__ = [
    "MessageType",
    "BaseMessage",
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ToolUse",
    "ToolResult",
    "Summary",
    "SystemMessage",
    "parse_message",
]
