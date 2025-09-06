"""
Checkpoint tracking implementation.

SINGLE RESPONSIBILITY: Track UUID-based message positions only.
No file I/O, no parsing, no business logic - just checkpoint state.
"""

from typing import Optional

from ...domain.interfaces.watch_interfaces import CheckpointTracker
from ...models import Message


class UUIDCheckpointTracker(CheckpointTracker):
    """UUID-based checkpoint tracker - single responsibility for position tracking."""

    def __init__(self, initial_checkpoint: Optional[str] = None):
        self._checkpoint_uuid = initial_checkpoint
        self._checkpoint_found = initial_checkpoint is None  # If no checkpoint, start from beginning

    def set_checkpoint(self, uuid: str) -> None:
        """Set checkpoint to specific message UUID."""
        self._checkpoint_uuid = uuid
        self._checkpoint_found = False  # Reset found flag

    def get_checkpoint(self) -> Optional[str]:
        """Get current checkpoint UUID."""
        return self._checkpoint_uuid

    def should_include_message(self, message: Message) -> bool:
        """Check if message should be included based on checkpoint."""
        if self._checkpoint_found:
            return True  # Include all messages after checkpoint

        # Haven't found checkpoint yet
        if self._checkpoint_uuid is None:
            return True  # No checkpoint set, include all

        if message.uuid == self._checkpoint_uuid:
            self._checkpoint_found = True
            return False  # Don't include the checkpoint message itself

        return False  # Skip messages before checkpoint
