"""SSE (Server-Sent Events) helper functions for streaming.

95/5 Principle: Dead simple SSE streaming for web frameworks.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Callable, Optional

import orjson
from loguru import logger

from ..models import Message
from .async_watcher import watch_async


async def stream_for_sse(
    file_path: str | Path, format_message: Optional[Callable[[Message], dict]] = None
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

    async for conv, new_messages in watch_async(file_path):
        for msg in new_messages:
            try:
                formatted = format_message(msg)
                yield {"data": orjson.dumps(formatted).decode("utf-8")}
            except Exception as e:
                logger.error(f"Error formatting message: {e}")
                continue

    # Send heartbeats during quiet periods
    while True:
        await asyncio.sleep(30)
        yield {"data": orjson.dumps({"type": "heartbeat"}).decode("utf-8")}


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
