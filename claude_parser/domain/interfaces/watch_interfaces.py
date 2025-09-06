"""
Watch domain interfaces - clean abstractions.

SOLID: Interface Segregation - focused, single-responsibility interfaces
DIP: High-level modules depend on these abstractions, not concrete implementations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Protocol

from ...models import Message
from ..entities.conversation import Conversation


class FileWatcher(Protocol):
    """Abstract interface for detecting file changes."""

    async def watch_for_changes(self, file_path: Path) -> AsyncGenerator[None, None]:
        """Watch file and yield when changes occur."""
        ...


class CheckpointTracker(Protocol):
    """Abstract interface for tracking message positions."""

    def set_checkpoint(self, uuid: str) -> None:
        """Set checkpoint to specific message UUID."""
        ...

    def get_checkpoint(self) -> Optional[str]:
        """Get current checkpoint UUID."""
        ...

    def should_include_message(self, message: Message) -> bool:
        """Check if message should be included based on checkpoint."""
        ...


class MessageStreamer(Protocol):
    """Abstract interface for streaming new messages."""

    async def stream_new_messages(
        self,
        file_path: Path,
        checkpoint_tracker: CheckpointTracker,
        message_types: Optional[List[str]] = None
    ) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
        """Stream new messages as they arrive."""
        ...


class WatchOrchestrator(Protocol):
    """High-level interface that coordinates all watch operations."""

    async def watch_file(
        self,
        file_path: Path,
        message_types: Optional[List[str]] = None,
        after_uuid: Optional[str] = None,
    ) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
        """Watch file and stream new messages - main coordination."""
        ...
