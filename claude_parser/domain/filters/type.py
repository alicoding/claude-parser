"""
Type-based message filter.

SOLID: Single Responsibility - Only type filtering.
"""

from ...models import Message


class TypeFilter:
    """Filter messages by type."""

    def __init__(self, message_type: type):
        """Initialize with message type to filter."""
        self.message_type = message_type

    def matches(self, message: Message) -> bool:
        """Check if message matches the specified type."""
        return isinstance(message, self.message_type)
