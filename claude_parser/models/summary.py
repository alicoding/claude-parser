"""
Summary message model.

SOLID: Single Responsibility - Summary messages only
DDD: Value object for conversation summaries
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import MessageType


class Summary(BaseModel):
    """Summary of conversation segment.

    Simplified model based on real JSONL structure:
    {"type":"summary","summary":"...","leafUuid":"..."}
    """

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, extra="allow"
    )

    type: MessageType = MessageType.SUMMARY
    summary: str = Field(..., min_length=1)
    leaf_uuid: Optional[str] = Field(None, alias="leafUuid")

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return f"Summary: {self.summary}"
