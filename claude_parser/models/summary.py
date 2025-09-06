"""
Summary message model.

SOLID: Single Responsibility - Summary messages only
DDD: Value object for conversation summaries
Framework: msgspec for serialization, domain logic preserved
"""

from typing import Optional
import msgspec

from ..msgspec_models import BaseMessage


class Summary(BaseMessage):
    """Summary of conversation segment - SOLID/DDD with msgspec framework.

    Simplified model based on real JSONL structure:
    {"type":"summary","summary":"...","leafUuid":"..."}
    """

    # SOLID: Summary specific fields only
    type: str = "summary"
    summary: str = ""
    leaf_uuid: Optional[str] = msgspec.field(name="leafUuid", default=None)

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return f"Summary: {self.summary}"
