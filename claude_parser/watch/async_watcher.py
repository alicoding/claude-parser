"""
Async JSONL file watcher - clean architecture with dependency injection.

SINGLE RESPONSIBILITY: Watch file + stream new messages as they come.
DIP: Depends on abstractions, not concrete implementations.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Optional

from ..domain.entities.conversation import Conversation
from ..domain.interfaces.data_processor import DataProcessor
from ..infrastructure.data import create_data_processor
from ..infrastructure.logger_config import logger
from ..models import Message


async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
    after_uuid: Optional[str] = None,
    data_processor: Optional[DataProcessor] = None,
) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
    """
    Watch a JSONL file and stream new messages as they come.

    Core capability: File watching + message streaming.
    Uses dependency injection - no concrete framework dependencies.

    Args:
        file_path: Path to JSONL file
        message_types: Optional filter ["user", "assistant", etc]
        stop_event: Optional event to stop watching
        after_uuid: Optional UUID to resume after
        data_processor: Optional data processor (injected for testing)

    Yields:
        (conversation, new_messages) on each change

    Example:
        async for conv, new_messages in watch_async("session.jsonl"):
            print(f"Got {len(new_messages)} new messages")
    """
    file_path = Path(file_path)

    # Wait for file creation if needed
    if not file_path.exists():
        logger.info(f"Waiting for {file_path.name} to be created...")
        while not file_path.exists():
            await asyncio.sleep(0.1)
            if stop_event and stop_event.is_set():
                return

    logger.info(f"Watching {file_path.name} for changes...")

    # Use dependency injection - clean architecture
    processor = data_processor or create_data_processor()
    last_conversation = None

    while True:
        if stop_event and stop_event.is_set():
            break

        try:
            if file_path.exists():
                # Parse messages using injected processor
                all_messages = processor.parser.parse_jsonl_file(file_path)

                # Build conversation with metadata
                current_conversation = processor.builder.build_conversation(all_messages, file_path)

                if last_conversation is None:
                    # First load - find new messages after checkpoint
                    new_messages = all_messages
                    if after_uuid:
                        new_messages = processor.filter.filter_after_uuid(new_messages, after_uuid)
                        after_uuid = None  # Only apply once
                else:
                    # Find truly new messages
                    new_messages = processor.filter.find_new_messages(
                        last_conversation.messages,
                        current_conversation.messages
                    )

                # Apply message type filter
                if message_types:
                    new_messages = processor.filter.filter_by_types(new_messages, message_types)

                if new_messages:
                    yield current_conversation, new_messages

                last_conversation = current_conversation

            await asyncio.sleep(0.1)  # Small delay

        except Exception as e:
            logger.error(f"Error watching file: {e}")
            await asyncio.sleep(1)


# Helper function removed - now handled by processor.filter.filter_after_uuid()
