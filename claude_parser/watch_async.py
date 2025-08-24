"""
Async watch wrapper - 95/5 principle for SSE streaming.

This module provides a dead-simple async interface for file watching,
perfect for SSE endpoints. Uses watchfiles' awatch which handles threading internally.

No manual threading needed - watchfiles runs Rust code in a separate thread!
"""

from typing import AsyncGenerator, Optional, List, Callable, Set
from pathlib import Path
import asyncio
from watchfiles import awatch, Change
from loguru import logger

from .infrastructure.jsonl_parser import parse_jsonl_streaming
from .models import Message, parse_message
from .domain.entities.conversation import Conversation, ConversationMetadata
from .infrastructure.message_repository import JsonlMessageRepository


async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    debounce: int = 100,  # 100ms debounce for rapid changes
    stop_event: Optional[asyncio.Event] = None
) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
    """
    Asynchronously watch a JSONL file and yield new messages.
    
    95/5 Principle: Dead simple async generator - no threading needed!
    
    Args:
        file_path: Path to JSONL file to monitor
        message_types: Optional filter for message types ["user", "assistant", etc]
        debounce: Milliseconds to wait before processing changes (default 100ms)
        stop_event: Optional asyncio.Event to stop watching
        
    Yields:
        Tuple of (full_conversation, new_messages) on each change
        
    Example:
        async for conv, new_messages in watch_async("session.jsonl"):
            for msg in new_messages:
                print(f"New message: {msg.type} - {msg.text_content}")
    """
    file_path = Path(file_path)
    if not file_path.exists():
        # Wait for file to be created if it doesn't exist
        logger.info(f"Waiting for {file_path.name} to be created...")
        async for changes in awatch(str(file_path.parent), stop_event=stop_event):
            if any(str(file_path) in path for _, path in changes):
                break
    
    # Track last position
    last_size = 0
    last_messages = []
    repo = JsonlMessageRepository()
    
    # Initial load if file exists
    if file_path.exists():
        messages = repo.load_messages(file_path)
        metadata = repo.get_metadata_from_messages(messages, file_path)
        conv = Conversation(messages, metadata)
        last_messages = messages.copy()
        last_size = file_path.stat().st_size
        
        # Yield initial state
        if messages:
            yield conv, messages
    
    logger.info(f"Watching {file_path.name} for changes...")
    
    # Watch for changes - awatch handles threading internally!
    async for changes in awatch(
        str(file_path),
        debounce=debounce,
        stop_event=stop_event,
        raise_interrupt=False  # Handle gracefully
    ):
        # Process only modified changes (not added/deleted)
        for change_type, path in changes:
            if change_type == Change.modified:
                try:
                    # Reload the file
                    current_messages = repo.load_messages(file_path)
                    current_size = file_path.stat().st_size
                    
                    # Detect file truncation/rotation
                    if current_size < last_size:
                        logger.info("File truncated/rotated, reloading from start")
                        last_messages = []
                    
                    # Find new messages
                    new_messages = current_messages[len(last_messages):]
                    
                    # Apply type filter if specified
                    if message_types and new_messages:
                        new_messages = [
                            msg for msg in new_messages 
                            if msg.type.value in message_types
                        ]
                    
                    if new_messages:
                        # Create fresh conversation with all messages
                        metadata = repo.get_metadata_from_messages(current_messages, file_path)
                        conv = Conversation(current_messages, metadata)
                        
                        # Yield the conversation and new messages
                        yield conv, new_messages
                        
                        # Update tracking
                        last_messages = current_messages
                        last_size = current_size
                        
                except Exception as e:
                    logger.error(f"Error processing file change: {e}")
                    # Continue watching despite errors


async def stream_for_sse(
    file_path: str | Path,
    format_message: Optional[Callable[[Message], dict]] = None
) -> AsyncGenerator[dict, None]:
    """
    Stream messages formatted for Server-Sent Events (SSE).
    
    Perfect for FastAPI EventSourceResponse endpoints.
    
    Args:
        file_path: Path to JSONL file
        format_message: Optional function to format messages
        
    Yields:
        Dicts with "data" key containing JSON-serializable message data
        
    Example:
        @app.get("/api/stream")
        async def stream():
            return EventSourceResponse(
                stream_for_sse("session.jsonl")
            )
    """
    import orjson
    
    if format_message is None:
        def format_message(msg: Message) -> dict:
            return {
                "type": msg.type.value,
                "uuid": msg.uuid,
                "timestamp": msg.timestamp,
                "content": msg.text_content,
                "sessionId": msg.session_id,
                "parentUuid": msg.parent_uuid
            }
    
    async for conv, new_messages in watch_async(file_path):
        for msg in new_messages:
            try:
                formatted = format_message(msg)
                yield {"data": orjson.dumps(formatted).decode('utf-8')}
            except Exception as e:
                logger.error(f"Error formatting message: {e}")
                continue
    
    # Send heartbeats during quiet periods
    while True:
        await asyncio.sleep(30)
        yield {"data": orjson.dumps({"type": "heartbeat"}).decode('utf-8')}


# 95/5 Principle: One-liner for SSE endpoints
async def create_sse_stream(file_path: str | Path) -> AsyncGenerator[dict, None]:
    """
    Dead simple SSE stream creator - one line in your FastAPI endpoint.
    
    Example:
        @app.get("/stream")
        async def stream():
            return EventSourceResponse(create_sse_stream("session.jsonl"))
    """
    async for event in stream_for_sse(file_path):
        yield event