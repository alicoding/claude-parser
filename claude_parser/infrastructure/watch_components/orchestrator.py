"""
Watch orchestrator - coordinates all watch components.

SINGLE RESPONSIBILITY: Coordinate file watching, checkpoint tracking, and message streaming.
DIP: Depends on abstractions, injects dependencies.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple

from ...domain.entities.conversation import Conversation
from ...domain.interfaces.data_processor import DataProcessor
from ...domain.interfaces.watch_interfaces import (
    CheckpointTracker,
    FileWatcher,
    MessageStreamer,
    WatchOrchestrator
)
from ...models import Message
from ..logger_config import logger
from .checkpoint_tracker import UUIDCheckpointTracker
from .file_watcher import WatchfilesFileWatcher
from .message_streamer import FileMessageStreamer


class FileWatchOrchestrator(WatchOrchestrator):
    """Orchestrates file watching components - dependency injection coordination."""

    def __init__(
        self,
        data_processor: DataProcessor,
        file_watcher: Optional[FileWatcher] = None,
        checkpoint_tracker_factory = UUIDCheckpointTracker,
        message_streamer_factory = FileMessageStreamer
    ):
        self._data_processor = data_processor
        self._file_watcher = file_watcher or WatchfilesFileWatcher()
        self._checkpoint_tracker_factory = checkpoint_tracker_factory
        self._message_streamer_factory = message_streamer_factory

    async def watch_file(
        self,
        file_path: Path,
        message_types: Optional[List[str]] = None,
        after_uuid: Optional[str] = None,
        stop_event: Optional[asyncio.Event] = None
    ) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
        """Watch file and coordinate all components."""

        # Create checkpoint tracker
        checkpoint_tracker = self._checkpoint_tracker_factory(after_uuid)

        # Create message streamer
        message_streamer = self._message_streamer_factory(self._data_processor)

        # Watch for file changes
        async for _ in self._file_watcher.watch_for_changes(file_path):
            if stop_event and stop_event.is_set():
                break

            try:
                # Stream new messages when file changes
                async for conversation, new_messages in message_streamer.stream_new_messages(
                    file_path, checkpoint_tracker, message_types
                ):
                    yield conversation, new_messages

            except Exception as e:
                logger.error(f"Error in watch orchestration: {e}")
                await asyncio.sleep(1)  # Brief pause on error
