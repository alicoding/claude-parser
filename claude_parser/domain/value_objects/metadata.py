"""
Conversation metadata value object.

SOLID: Single Responsibility - Only metadata representation.
DDD: Value Object - Immutable, no identity.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class ConversationMetadata:
    """Value object for conversation metadata."""

    session_id: Optional[str]
    filepath: Path
    current_dir: Optional[str]
    git_branch: Optional[str]
    message_count: int
    error_count: int
