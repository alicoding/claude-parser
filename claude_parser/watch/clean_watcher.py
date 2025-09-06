"""
Clean watch implementation - replaces the entire messy watch domain.

CLEAN ARCHITECTURE:
- Uses abstractions and dependency injection
- Single place for framework coordination
- Maintains exact same public API
- SRP: Each component has single responsibility
- DIP: Depends on abstractions, not concretions
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple

from ..domain.entities.conversation import Conversation
from ..domain.interfaces.data_processor import DataProcessor
from ..infrastructure.data_processing import create_data_processor
from ..infrastructure.watch_components import FileWatchOrchestrator
from ..models import Message


async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
    after_uuid: Optional[str] = None,
) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
    """
    Watch a JSONL file and stream new messages - clean architecture implementation.

    Replaces the entire complex watch domain with clean, single-responsibility components.

    Architecture:
    - FileWatcher: Detects changes using watchfiles framework
    - CheckpointTracker: Manages UUID-based positions
    - MessageStreamer: Streams new messages using DataProcessor
    - WatchOrchestrator: Coordinates all components with DI

    Args:
        file_path: Path to JSONL file
        message_types: Optional filter ["user", "assistant", etc]
        stop_event: Optional event to stop watching
        after_uuid: Optional UUID to resume after

    Yields:
        (conversation, new_messages) on each change

    Example:
        async for conv, new_messages in watch_async("session.jsonl"):
            print(f"Got {len(new_messages)} new messages")
    """
    file_path = Path(file_path)

    # Create data processor using factory
    data_processor = create_data_processor()

    # Create orchestrator with dependency injection
    orchestrator = FileWatchOrchestrator(data_processor)

    # Delegate to orchestrator - clean separation of concerns
    async for conversation, new_messages in orchestrator.watch_file(
        file_path=file_path,
        message_types=message_types,
        after_uuid=after_uuid,
        stop_event=stop_event
    ):
        yield conversation, new_messages


def watch(
    file_path: str | Path,
    callback,
    message_types: Optional[List[str]] = None,
    after_uuid: Optional[str] = None,
):
    """
    Sync wrapper around async watch - maintains API compatibility.

    Args:
        file_path: Path to JSONL file
        callback: Function called with (conversation, new_messages)
        message_types: Optional filter ["user", "assistant", etc]
        after_uuid: Optional UUID to resume after

    Example:
        def on_new(conv, new_messages):
            print(f"Got {len(new_messages)} new messages")

        watch("session.jsonl", on_new)
    """
    async def _async_watch():
        async for conversation, new_messages in watch_async(
            file_path, message_types, after_uuid=after_uuid
        ):
            callback(conversation, new_messages)

    # Run async function in sync context
    asyncio.run(_async_watch())
