"""
Simplified watch implementation - SINGLE place for watchfiles usage.

95/5 Principle: 95% frameworks (watchfiles + existing load()) + 5% glue.
DIP: This IS the single centralized place. Everyone else uses this.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple

import watchfiles

from ..application.conversation_service import load
from ..domain.entities.conversation import Conversation
from ..infrastructure.logger_config import logger
from ..models import Message


async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
    after_uuid: Optional[str] = None,
) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
    """
    Watch a JSONL file and stream new messages - SINGLE centralized place.

    95/5 Implementation:
    - 95% frameworks: watchfiles + existing load() function
    - 5% glue: simple filtering and change detection

    This IS the centralized watch feature. Everyone else should use this,
    not bypass to lower levels.

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

    # Wait for file creation if needed
    if not file_path.exists():
        logger.info(f"Waiting for {file_path.name} to be created...")
        async for changes in watchfiles.awatch(str(file_path.parent), stop_event=stop_event):
            if any(str(file_path) in path for _, path in changes):
                break

    logger.info(f"Watching {file_path.name} for changes...")

    last_conversation = None
    checkpoint_found = after_uuid is None

    # Watch for file changes using watchfiles framework
    async for changes in watchfiles.awatch(str(file_path), stop_event=stop_event):
        try:
            # Use existing load() function - 95% framework
            current_conversation = load(file_path)

            if last_conversation is None:
                # First load - apply checkpoint and filters
                new_messages = current_conversation.messages

                # Apply UUID checkpoint filter
                if not checkpoint_found:
                    filtered_messages = []
                    for msg in new_messages:
                        if msg.uuid == after_uuid:
                            checkpoint_found = True
                            continue  # Don't include checkpoint message
                        if checkpoint_found:
                            filtered_messages.append(msg)
                    new_messages = filtered_messages

            else:
                # Find truly new messages since last conversation
                if len(current_conversation.messages) > len(last_conversation.messages):
                    new_messages = current_conversation.messages[len(last_conversation.messages):]
                else:
                    new_messages = []

            # Apply message type filter
            if message_types:
                new_messages = [
                    msg for msg in new_messages
                    if msg.type.value in message_types
                ]

            if new_messages:
                last_conversation = current_conversation
                yield current_conversation, new_messages

        except Exception as e:
            logger.error(f"Error watching file: {e}")
            await asyncio.sleep(1)


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
