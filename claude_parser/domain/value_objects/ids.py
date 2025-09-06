"""Identity value objects for domain entities.

DDD: Strongly-typed identifiers to eliminate primitive obsession.
SOLID: Immutable value objects with validation.
95/5: Uses uuid library for UUID validation and generation.
"""

from typing import NewType, Union
from dataclasses import dataclass
from uuid import UUID, uuid4
import re


@dataclass(frozen=True)
class SessionId:
    """Session identifier value object.

    DDD: Value object for session identity
    Validation: Must be valid UUID format

    Example:
        session = SessionId("8f64b245-7268-4ecd-9b90-34037f3c5b75")
        new_session = SessionId.generate()
    """
    value: str

    def __post_init__(self):
        """Validate session ID format."""
        if not self.value:
            raise ValueError("Session ID cannot be empty")

        # Must be UUID format or valid session identifier
        if not self._is_valid_format(self.value):
            raise ValueError(f"Invalid session ID format: {self.value}")

    def _is_valid_format(self, value: str) -> bool:
        """Check if value is valid session ID format."""
        try:
            # Try UUID format first
            UUID(value)
            return True
        except ValueError:
            # Fall back to basic validation for session-like strings
            return bool(re.match(r'^[a-zA-Z0-9\-_]{3,}$', value))

    @classmethod
    def generate(cls) -> 'SessionId':
        """Generate new random session ID."""
        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class MessageUuid:
    """Message UUID value object.

    DDD: Value object for message identity
    Validation: Must be valid UUID or message ID format

    Example:
        msg_id = MessageUuid("msg-123")
        uuid_id = MessageUuid("550e8400-e29b-41d4-a716-446655440000")
    """
    value: str

    def __post_init__(self):
        """Validate message UUID format."""
        if not self.value:
            raise ValueError("Message UUID cannot be empty")

        if not self._is_valid_format(self.value):
            raise ValueError(f"Invalid message UUID format: {self.value}")

    def _is_valid_format(self, value: str) -> bool:
        """Check if value is valid message UUID format."""
        try:
            # Try UUID format first
            UUID(value)
            return True
        except ValueError:
            # Fall back to msg-* pattern or similar
            return bool(re.match(r'^[a-zA-Z0-9\-_]{1,}$', value))

    @classmethod
    def generate(cls) -> 'MessageUuid':
        """Generate new random message UUID."""
        return cls(str(uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class AgentId:
    """Agent identifier value object.

    DDD: Value object for agent identity
    Used to distinguish between main agent and sub-agents

    Example:
        main_agent = AgentId("main")
        sub_agent = AgentId("sub-456")
    """
    value: str

    def __post_init__(self):
        """Validate agent ID format."""
        if not self.value:
            raise ValueError("Agent ID cannot be empty")

        if not re.match(r'^[a-zA-Z0-9\-_]{1,50}$', self.value):
            raise ValueError(f"Invalid agent ID format: {self.value}")

    def __str__(self) -> str:
        return self.value


# Type aliases for backward compatibility and clarity
SessionIdType = Union[SessionId, str]
MessageUuidType = Union[MessageUuid, str]
AgentIdType = Union[AgentId, str]


__all__ = [
    "SessionId",
    "MessageUuid",
    "AgentId",
    "SessionIdType",
    "MessageUuidType",
    "AgentIdType",
]
