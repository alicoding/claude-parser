"""
Watch service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

import asyncio
import json
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple, Callable
from ..core.resources import get_resource_manager
from ..components.file_watcher import FileWatcher
from ..components.message_differ import MessageDiffer
from ..application.conversation_service import load
from ..domain.entities.conversation import Conversation
from ..models import Message
from ..infrastructure.logger_config import logger


class WatchService:
    """Clean watch service using ResourceManager pattern."""

    def __init__(self):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        self.file_watcher = FileWatcher(self.resources)
        self.message_differ = MessageDiffer(self.resources)

    async def watch_messages(
        self,
        file_path: str | Path,
        message_types: Optional[List[str]] = None,
        stop_event: Optional[asyncio.Event] = None,
        after_uuid: Optional[str] = None,
    ) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
        """Watch file and yield new messages using micro-components."""
        file_path = Path(file_path)
        last_conversation = None

        async for _ in self.file_watcher.watch_file_changes(file_path, stop_event):
            try:
                # Load current conversation
                current_conversation = load(file_path)

                # Find new messages using micro-component
                new_messages = self.message_differ.find_new_messages(
                    current_conversation,
                    last_conversation,
                    after_uuid
                )

                # Apply message type filter
                if message_types and new_messages:
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

    async def stream_for_sse(
        self,
        file_path: str | Path,
        format_message: Optional[Callable[[Message], dict]] = None
    ) -> AsyncGenerator[dict, None]:
        """Stream messages for SSE using clean architecture."""
        if format_message is None:
            def format_message(msg: Message) -> dict:
                return {
                    "type": msg.type.value,
                    "uuid": msg.uuid,
                    "timestamp": msg.timestamp,
                    "content": msg.text_content,
                    "sessionId": msg.session_id,
                    "parentUuid": msg.parent_uuid,
                }

        async for conv, new_messages in self.watch_messages(file_path):
            for msg in new_messages:
                try:
                    formatted = format_message(msg)
                    yield {"data": json.dumps(formatted)}
                except Exception as e:
                    logger.error(f"Error formatting message: {e}")
                    continue


# 95/5 Factory Functions (Public API)
async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
    after_uuid: Optional[str] = None,
) -> AsyncGenerator[Tuple[Conversation, List[Message]], None]:
    """Watch file asynchronously - 95% use case."""
    service = WatchService()
    async for conv, messages in service.watch_messages(file_path, message_types, stop_event, after_uuid):
        yield conv, messages


def watch(
    file_path: str | Path,
    callback,
    message_types: Optional[List[str]] = None,
    after_uuid: Optional[str] = None,
):
    """Sync wrapper around async watch - 5% use case."""
    async def _async_watch():
        async for conversation, new_messages in watch_async(
            file_path, message_types, after_uuid=after_uuid
        ):
            callback(conversation, new_messages)

    asyncio.run(_async_watch())


async def stream_for_sse(
    file_path: str | Path,
    format_message: Optional[Callable[[Message], dict]] = None
) -> AsyncGenerator[dict, None]:
    """Stream for SSE - 95% use case."""
    service = WatchService()
    async for event in service.stream_for_sse(file_path, format_message):
        yield event


async def create_sse_stream(file_path: str | Path) -> AsyncGenerator[dict, None]:
    """Simple SSE stream - 95% use case."""
    async for event in stream_for_sse(file_path):
        yield event
