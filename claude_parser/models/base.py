"""
Base message models.

SOLID: Single Responsibility - Base message structure only
DDD: Base value object for all messages
"""

from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, ConfigDict
import pendulum


class MessageType(str, Enum):
    """Message types in Claude conversations."""
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SUMMARY = "summary"
    SYSTEM = "system"


class BaseMessage(BaseModel):
    """Base class for all message types in Claude JSONL format.
    
    All Claude conversations are stored as JSONL (JSON Lines) where each
    line represents a single message in the conversation.
    """
    
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra="allow"
    )
    
    type: MessageType = Field(
        description="Message type: user, assistant, tool_use, tool_result, summary, or system"
    )
    uuid: Optional[str] = Field(
        None,
        alias="uuid",
        description="Unique identifier for this message"
    )
    parent_uuid: Optional[str] = Field(
        None, 
        alias="parentUuid",
        description="UUID of parent message for threading/branching conversations"
    )
    session_id: Optional[str] = Field(
        None,
        alias="sessionId", 
        description="Session identifier for grouping related messages"
    )
    
    timestamp: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp when message was created"
    )
    
    @property
    def text_content(self) -> str:
        """Get text content of message for searching."""
        return ""
    
    @property
    def parsed_timestamp(self):
        """Parse timestamp if present."""
        if self.timestamp:
            return pendulum.parse(self.timestamp)
        return None


# Type alias for any message
Message = Union[
    "UserMessage", 
    "AssistantMessage", 
    "ToolUse", 
    "ToolResult", 
    "Summary", 
    "SystemMessage"
]