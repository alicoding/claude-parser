"""
System message model.

SOLID: Single Responsibility - System messages only
DDD: Value object for system messages
Framework: msgspec for serialization, domain logic preserved
"""

from typing import Optional
import msgspec

class SystemMessage(msgspec.Struct, tag="system", kw_only=True):
    """System message (prompts, instructions)."""

    # Core identification (DRY: shared across all messages)
    uuid: str
    parent_uuid: Optional[str] = msgspec.field(name="parentUuid", default=None)
    session_id: str = msgspec.field(name="sessionId")

    # Context fields (DRY: shared across all messages)
    cwd: str = ""
    git_branch: str = msgspec.field(name="gitBranch", default="")
    timestamp: Optional[str] = None

    # SOLID: SystemMessage specific fields
    content: str = ""

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        return f"System: {self.content}"

    @property
    def parsed_timestamp(self) -> Optional[str]:
        """DRY: Shared timestamp parsing logic."""
        return self.timestamp
