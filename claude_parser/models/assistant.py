"""
Assistant message model.

SOLID: Single Responsibility - Assistant messages only
DDD: Value object for assistant messages
Framework: msgspec for serialization, domain logic preserved
"""

from typing import Optional, Dict, Any
import msgspec

from ..utils import has_message_dict, get_message_content
from ..msgspec_models import BaseMessage


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
        """Get searchable text content from real JSONL structure."""
        # Use utility function to get content
        content = get_message_content(self)
        if content:
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            text_parts.append(f"Tool: {block.get('name', 'unknown')}")
                return " ".join(text_parts)
            elif isinstance(content, str):
                return content

        # Fallback to direct content field
        return getattr(self, "content", "")

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens from real JSONL structure."""
        # First try real production data structure
        if has_message_dict(self):
            usage = self.message.get("usage", {})
            if usage:
                return (
                    usage.get("input_tokens", 0)
                    + usage.get("output_tokens", 0)
                    + usage.get("cache_read_input_tokens", 0)
                    + usage.get("cache_creation_input_tokens", 0)
                )

        # Fallback to old structure
        return (
            (self.input_tokens or 0)
            + (self.output_tokens or 0)
            + (self.cache_read_tokens or 0)
            + (self.cache_write_tokens or 0)
        )

    @property
    def real_usage_info(self) -> dict:
        """Get real production usage info from nested message structure."""
        if has_message_dict(self):
            return self.message.get("usage", {})
        return {}

    @property
    def tool_uses(self) -> list:
        """Get tool use blocks from message content."""
        content = get_message_content(self)
        if isinstance(content, list):
            return [
                block
                for block in content
                if isinstance(block, dict) and block.get("type") == "tool_use"
            ]
        return []

    @property
    def parsed_timestamp(self) -> Optional[str]:
        """DRY: Shared timestamp parsing logic."""
        return self.timestamp
