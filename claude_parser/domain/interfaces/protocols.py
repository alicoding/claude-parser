"""
Domain interfaces and protocols.

SOLID: Interface Segregation - Small, focused interfaces.
DRY: Shared contracts for domain operations.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Protocol

from ...models import Message


class MessageFilter(Protocol):
    """Strategy pattern for message filtering."""

    def matches(self, message: Message) -> bool:
        """Check if message matches filter criteria."""
        ...


class MessageRepository(ABC):
    """Repository pattern for message data access."""

    @abstractmethod
    def load_messages(self, filepath: Path) -> List[Message]:
        """Load messages from data source."""
        ...
