"""
User message model.

SOLID: Single Responsibility - User messages only
DDD: Value object for user messages
"""

from typing import Optional
from pydantic import Field

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
        """Get searchable text content."""
        return self.content