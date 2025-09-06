"""
Message streaming implementation.

SINGLE RESPONSIBILITY: Stream new messages from file.
Uses DataProcessor abstraction - no direct framework dependencies.
"""

from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple

from ...domain.entities.conversation import Conversation
from ...domain.interfaces.data_processor import DataProcessor
from ...domain.interfaces.watch_interfaces import CheckpointTracker, MessageStreamer
from ...models import Message
from ..logger_config import logger


class FileMessageStreamer(MessageStreamer):
    """Stream messages from file - delegates parsing to DataProcessor."""

    def __init__(self, data_processor: DataProcessor):
        self._data_processor = data_processor
        self._last_conversation: Optional[Conversation] = None

    async def stream_new_messages(
        self,
        file_path: Path,
        checkpoint_tracker: CheckpointTracker,
        message_types: Optional[List[str]] = None
    ) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
        """Stream new messages using data processor abstraction."""

        try:
            # Parse all messages using data processor
            all_messages = self._data_processor.parser.parse_jsonl_file(file_path)

            # Build current conversation
            current_conversation = self._data_processor.builder.build_conversation(all_messages, file_path)

            # Find new messages
            if self._last_conversation is None:
                # First load - apply checkpoint filter
                new_messages = [
                    msg for msg in all_messages
                    if checkpoint_tracker.should_include_message(msg)
                ]
            else:
                # Find truly new messages since last conversation
                new_messages = self._data_processor.filter.find_new_messages(
                    self._last_conversation.messages,
                    current_conversation.messages
                )

            # Apply message type filter
            if message_types:
                new_messages = self._data_processor.filter.filter_by_types(new_messages, message_types)

            if new_messages:
                self._last_conversation = current_conversation
                yield current_conversation, new_messages

        except Exception as e:
            logger.error(f"Error streaming messages: {e}")
            raise
