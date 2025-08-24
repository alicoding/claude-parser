"""
Summary message model.

SOLID: Single Responsibility - Summary messages only
DDD: Value object for conversation summaries
"""

from typing import Optional
from pydantic import Field

from .base import BaseMessage, MessageType


class Summary(BaseMessage):
    """Summary of conversation segment."""
    
    type: MessageType = MessageType.SUMMARY
    summary: str = Field(..., min_length=1)
    leaf_uuid: Optional[str] = Field(None, alias="leafUuid")
    
    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return f"Summary: {self.summary}"