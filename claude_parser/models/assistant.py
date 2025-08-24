"""
Assistant message model.

SOLID: Single Responsibility - Assistant messages only
DDD: Value object for assistant messages
"""

from typing import Optional
from pydantic import Field

from .base import BaseMessage, MessageType


class AssistantMessage(BaseMessage):
    """Assistant (Claude) message in conversation."""
    
    type: MessageType = MessageType.ASSISTANT
    content: str = Field(default="")  # Can be empty for tool-only messages
    
    # Token tracking
    input_tokens: Optional[int] = Field(None, alias="inputTokens")
    output_tokens: Optional[int] = Field(None, alias="outputTokens")
    cache_read_tokens: Optional[int] = Field(None, alias="cacheReadTokens")
    cache_write_tokens: Optional[int] = Field(None, alias="cacheWriteTokens")
    
    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return self.content
    
    @property
    def total_tokens(self) -> int:
        """Calculate total tokens used."""
        return (
            (self.input_tokens or 0) +
            (self.output_tokens or 0) +
            (self.cache_read_tokens or 0) +
            (self.cache_write_tokens or 0)
        )