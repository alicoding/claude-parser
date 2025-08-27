"""
User message model.

SOLID: Single Responsibility - User messages only
DDD: Value object for user messages
"""

from typing import Optional

from pydantic import Field

from ..utils import get_message_content
from .base import BaseMessage, MessageType


class UserMessage(BaseMessage):
    """User message in conversation."""

    type: MessageType = MessageType.USER
    content: str = Field(default="")  # Can be empty in some cases

    # Context fields
    cwd: Optional[str] = Field(None, description="Current working directory")
    git_branch: Optional[str] = Field(None, alias="gitBranch")

    # Tool approval
    tool_approval: Optional[str] = Field(None, alias="toolApproval")

    @property
    def text_content(self) -> str:
        """Get searchable text content from real JSONL structure."""
        # Use utility function to get content
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
