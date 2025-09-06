"""
User message model.

SOLID: Single Responsibility - User messages only
DDD: Value object for user messages
Framework: msgspec for serialization, domain logic preserved
"""

from typing import Optional
import msgspec

from ..utils import get_message_content
from ..msgspec_models import BaseMessage


class UserMessage(BaseMessage, tag="user"):
    """User message in conversation - SOLID/DDD with msgspec framework."""

    # SOLID: UserMessage specific fields only
    content: str = ""  # Can be empty in some cases

    # Tool approval (user-specific behavior)
    tool_approval: Optional[str] = msgspec.field(name="toolApproval", default=None)

    @property
    def text_content(self) -> str:
        """SOLID: User-specific content extraction logic."""
        # DRY: Use existing utility function
        content = get_message_content(self)
        if content:
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                # Handle content blocks (tool results, etc.)
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_result":
                            text_parts.append(str(block.get("content", "")))
                        elif "text" in block:
                            text_parts.append(block["text"])
                return " ".join(text_parts)

        # Fallback to direct content field
        return getattr(self, "content", "")

    @property
    def parsed_timestamp(self) -> Optional[str]:
        """DRY: Shared timestamp parsing logic."""
        return self.timestamp
