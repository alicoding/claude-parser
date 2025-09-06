"""
Streaming Service - Application Layer.

Provides backend-agnostic streaming using watch domain.
Works with any async framework (FastAPI, Sanic, aiohttp, Quart, etc).

SOLID:
- SRP: Single responsibility - message streaming
- DIP: Depends on watch domain abstractions
- OCP: Open for extension via formatters
"""

from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, Optional, Union

import json
from ..infrastructure.logger_config import logger

from ..models import Message
from ..watch import watch_async, stream_for_sse, create_sse_stream


class StreamFormat(str, Enum):
    """Supported streaming formats."""

    JSON = "json"  # Raw JSON objects
    SSE = "sse"  # Server-Sent Events format
    NDJSON = "ndjson"  # Newline-delimited JSON
    RAW = "raw"  # Raw Python dicts


class StreamingService:
    """
    Backend-agnostic streaming service.

    Works with any async Python web framework.
    """

    @staticmethod
    def default_formatter(msg: Message) -> Dict[str, Any]:
        """Default message formatter."""
        return {
            "type": msg.type.value,
            "uuid": msg.uuid,
            "timestamp": msg.timestamp,
            "content": msg.text_content,
            "sessionId": msg.session_id,
            "parentUuid": msg.parent_uuid,
        }

    async def stream_messages(
        self,
        file_path: str | Path,
        format: StreamFormat = StreamFormat.RAW,
        message_types: Optional[list[str]] = None,
        formatter: Optional[Callable[[Message], Dict]] = None,
    ) -> AsyncGenerator[Union[Dict, str, bytes], None]:
        """
        Stream messages in various formats.

        Backend-agnostic - works with any async framework.

        Args:
            file_path: Path to JSONL file
            format: Output format (raw, json, sse, ndjson)
            message_types: Optional filter for message types
            formatter: Optional message formatter function

        Yields:
            Formatted messages based on format parameter

        Examples:
            # FastAPI with SSE
            @app.get("/stream")
            async def stream():
                service = StreamingService()
                async def generate():
                    async for event in service.stream_messages("session.jsonl", format=StreamFormat.SSE):
                        yield event
                return EventSourceResponse(generate())

            # aiohttp with NDJSON
            async def stream(request):
                response = web.StreamResponse()
                await response.prepare(request)
                service = StreamingService()
                async for line in service.stream_messages("session.jsonl", format=StreamFormat.NDJSON):
                    await response.write(line.encode())
                return response

            # Sanic with JSON streaming
            @app.route("/stream")
            async def stream(request):
                async def generate():
                    service = StreamingService()
                    async for data in service.stream_messages("session.jsonl", format=StreamFormat.JSON):
                        yield data
                return stream(generate)
        """
        if formatter is None:
            formatter = self.default_formatter

        try:
            async for conv, new_messages in watch_async(file_path, message_types):
                for msg in new_messages:
                    try:
                        formatted = formatter(msg)

                        # Format based on output type
                        if format == StreamFormat.RAW:
                            yield formatted
                        elif format == StreamFormat.JSON:
                            yield json.dumps(formatted)
                        elif format == StreamFormat.SSE:
                            # Use centralized SSE formatting from sse_helpers
                            yield f"data: {json.dumps(formatted)}\n\n"
                        elif format == StreamFormat.NDJSON:
                            # Newline-delimited JSON
                            yield json.dumps(formatted) + "\n"

                    except Exception as e:
                        logger.error(f"Error formatting message: {e}")
                        continue

        except Exception as e:
            logger.error(f"Stream error: {e}")
            # Send error in appropriate format
            error_data = {"type": "error", "message": str(e)}

            if format == StreamFormat.RAW:
                yield error_data
            elif format == StreamFormat.JSON:
                yield ororjson.dumps(error_data).decode('utf-8').decode("utf-8")
            elif format == StreamFormat.SSE:
                yield f"data: {orjson.dumps(error_data).decode('utf-8')}\n\n"
            elif format == StreamFormat.NDJSON:
                yield orjson.dumps(error_data).decode("utf-8") + "\n"

    async def stream_with_heartbeat(
        self, file_path: str | Path, heartbeat_interval: int = 30, **kwargs
    ) -> AsyncGenerator[Dict[str, str], None]:
        """
        Stream with periodic heartbeats.

        Keeps SSE connection alive during quiet periods.
        """
        import asyncio

        queue = asyncio.Queue()

        async def watch_task():
            """Background task to watch file."""
            async for conv, new_messages in watch_async(
                file_path, kwargs.get("message_types")
            ):
                for msg in new_messages:
                    await queue.put(msg)

        # Start watcher in background
        task = asyncio.create_task(watch_task())

        try:
            formatter = kwargs.get("formatter", self.default_formatter)

            while True:
                try:
                    # Wait for message with timeout
                    msg = await asyncio.wait_for(
                        queue.get(), timeout=float(heartbeat_interval)
                    )
                    formatted = formatter(msg)
                    yield {"data": json.dumps(formatted)}

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield {"data": json.dumps({"type": "heartbeat"})}

        finally:
            task.cancel()


# ==========================================
# 95/5 FACTORY FUNCTIONS (Main API)
# ==========================================


async def create_sse_stream(
    file_path: str | Path, message_types: Optional[list[str]] = None
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Create SSE event stream from JSONL file.

    95/5 Principle: Uses centralized sse_helpers!

    Example:
        @app.get("/stream")
        async def stream():
            return EventSourceResponse(
                create_sse_stream("session.jsonl")
            )
    """
    # Use centralized SSE functionality from watch domain
    async for event in stream_for_sse(file_path):
        yield event


async def create_sse_stream_with_heartbeat(
    file_path: str | Path, **kwargs
) -> AsyncGenerator[Dict[str, str], None]:
    """
    Create SSE stream with heartbeat support.

    Uses StreamingService for heartbeat functionality.
    """
    # Use the StreamingService for heartbeat functionality
    service = StreamingService()
    async for event in service.stream_with_heartbeat(file_path, **kwargs):
        yield event
