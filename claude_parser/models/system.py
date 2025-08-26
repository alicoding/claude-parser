"""
System message model.

SOLID: Single Responsibility - System messages only
DDD: Value object for system messages
"""

from pydantic import Field

from .base import BaseMessage, MessageType


class SystemMessage(BaseMessage):
    """System message (prompts, instructions)."""

    type: MessageType = MessageType.SYSTEM
    content: str = Field(..., min_length=1)

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return f"System: {self.content}"
