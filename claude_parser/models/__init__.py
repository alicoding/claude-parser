"""
Message models for Claude Parser - migrated to msgspec.

SOLID: Each model in its own file
DDD: Clear message types as value objects
Framework: msgspec for serialization, domain logic preserved
"""

# BaseMessage is now implemented directly in each message class
# This follows msgspec tagged struct pattern

# Import migrated message types
from .assistant import AssistantMessage

from .system import SystemMessage
from .summary import Summary
from .tool import ToolUseMessage, ToolResultMessage
from .user import UserMessage

# Legacy imports that haven't been migrated yet
from .content import ContentBlock, ToolResultContent, ToolUseContent
from .usage import UsageInfo

# Define Message Union with actual classes (no forward references)
from typing import Union
from enum import Enum

class MessageType(str, Enum):
    """Message type enumeration for backward compatibility."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SUMMARY = "summary"

Message = Union[
    UserMessage,
    AssistantMessage,
    SystemMessage,
    ToolUseMessage,
    ToolResultMessage,
    Summary,
]

__all__ = [
    "Message",
    "MessageType",
    "UserMessage",
    "AssistantMessage",
    "SystemMessage",
    "ToolUseMessage",
    "ToolResultMessage",
    "Summary",
    "ContentBlock",
    "ToolUseContent",
    "ToolResultContent",
    "UsageInfo",
]
