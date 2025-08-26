"""
Base message models.

SOLID: Single Responsibility - Base message structure only
DDD: Base value object for all messages
"""

from enum import Enum
from typing import List, Optional, Union, TYPE_CHECKING

import pendulum
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .user import UserMessage
    from .assistant import AssistantMessage
    from .system import SystemMessage
    from .summary import Summary
    from .tool import ToolUseMessage, ToolResultMessage


class MessageType(str, Enum):
    """Message types in Claude conversations.

    Based on analysis of 41,085 real messages plus test requirements:
    - user, assistant, system, summary are core message types
    - tool_use/tool_result added for test compatibility and future support
    """

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    SUMMARY = "summary"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"


class BaseMessage(BaseModel):
    """Base class for all message types in Claude JSONL format.

    Based on analysis of 41,085 real Claude Code messages.
    All fields match the actual JSONL structure from docs/JSONL_STRUCTURE.md
    """

    model_config = ConfigDict(
        populate_by_name=True, str_strip_whitespace=True, extra="allow"
    )

    # Core message identification (100% occurrence rate)
    type: MessageType = Field(
        description="Message type: user, assistant, system, or summary"
    )
    uuid: str = Field(description="Unique identifier for this message (always present)")
    parent_uuid: Optional[str] = Field(
        None,
        alias="parentUuid",
        description="UUID of parent message (null for first message)",
    )
    session_id: str = Field(
        alias="sessionId",
        description="Session identifier (changes without --resume/--continue)",
    )

    # Context fields (100% occurrence rate in real data, optional in tests)
    cwd: str = Field(default="", description="Current working directory")
    git_branch: str = Field(
        default="",
        alias="gitBranch",
        description="Git branch (empty string for non-git directories)",
    )
    version: str = Field(
        default="unknown", description="Claude Code version (e.g., '1.0.83')"
    )

    # Metadata (100% occurrence rate in real data, optional in tests)
    timestamp: Optional[str] = Field(
        default=None, description="ISO 8601 timestamp when message was created"
    )
    is_sidechain: bool = Field(
        default=False,
        alias="isSidechain",
        description="True if part of parallel exploration",
    )
    user_type: str = Field(
        default="external",
        alias="userType",
        description="User type (always 'external' in user files)",
    )

    # Optional metadata
    is_meta: Optional[bool] = Field(
        None,
        alias="isMeta",
        description="True for meta messages (system notifications)",
    )
    is_compact_summary: Optional[bool] = Field(
        None, alias="isCompactSummary", description="True for compact summary messages"
    )
    is_api_error_message: Optional[bool] = Field(
        None, alias="isApiErrorMessage", description="True for API error messages"
    )

    # Tool-related (for linking tool use to results)
    tool_use_id: Optional[str] = Field(
        None, alias="toolUseID", description="Links tool use to result"
    )
    tool_use_result: Optional[Union[dict, str, List[dict]]] = Field(
        None,
        alias="toolUseResult",
        description="Tool result: dict (simple), string (error), or List[ContentBlock] (structured)",
    )

    # Request tracking (assistant messages)
    request_id: Optional[str] = Field(
        None, alias="requestId", description="API request ID"
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


# Type alias for any message (based on real JSONL structure + test requirements)
Message = Union[
    "UserMessage",
    "AssistantMessage",
    "SystemMessage",
    "Summary",
    "ToolUseMessage",
    "ToolResultMessage",
]
