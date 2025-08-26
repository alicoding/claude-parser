"""
TRUE 95/5 JSONL Streaming Implementation.

Following the pattern alignment principle:
- watchfiles: Tells us WHEN something changed (like inotify)
- aiofiles: Async file I/O without blocking
- orjson: Fast JSON parsing (we already use it everywhere)
- Our code: Just glue - tracking position, detecting rotation

This is like using Temporal for workflows - the library IS the pattern.
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List

import aiofiles
import orjson
from loguru import logger
from watchfiles import awatch


class StreamingJSONLReader:
    """
    TRUE 95/5 streaming reader for JSONL files.

    Handles:
    - Incremental reading (only new lines)
    - File rotation detection
    - Position tracking (like tail -f)
    - Large file support (no full reload)
    """

    def __init__(self, filepath: Path | str):
        """Initialize with just a filepath - TRUE 95/5 simplicity."""
        self.filepath = Path(filepath)
        self.position = 0
        self.last_size = 0

    async def get_new_messages(self) -> List[Dict[str, Any]]:
        """
        Get new messages since last read.

        TRUE 95/5: Simple method that does one thing well.
        """
        messages = []

        # Check if file exists
        if not self.filepath.exists():
            return messages

        try:
            async with aiofiles.open(self.filepath, "rb") as f:
                # Check file size for rotation detection
                await f.seek(0, 2)  # Seek to end
                current_size = await f.tell()

                # Detect rotation (file got smaller)
                if current_size < self.last_size:
                    logger.info(f"File rotation detected for {self.filepath}")
                    self.position = 0

                # Seek to last position
                await f.seek(self.position)

                # Read new lines
                async for line in f:
                    try:
                        # Parse JSON line
                        data = orjson.loads(line)
                        messages.append(data)
                    except Exception as e:
                        logger.warning(f"Failed to parse line: {e}")
                        continue

                # Update position
                self.position = await f.tell()
                self.last_size = current_size

        except Exception as e:
            logger.error(f"Error reading file: {e}")

        return messages


async def stream_jsonl_incrementally(
    filepath: Path | str, watch: bool = True
) -> AsyncGenerator[List[Dict[str, Any]], None]:
    """
    TRUE 95/5 streaming function - dead simple API.

    Just like LlamaIndex.from_documents() or Temporal.workflow(),
    this function does EVERYTHING with minimal config.

    Args:
        filepath: Path to JSONL file
        watch: If True, watch for changes. If False, just read once.

    Yields:
        List of new messages each time file changes
    """
    reader = StreamingJSONLReader(filepath)
    filepath = Path(filepath)

    # Always do initial read if file exists
    if filepath.exists():
        messages = await reader.get_new_messages()
        if messages:
            yield messages

    if not watch:
        return

    # Watch for changes
    try:
        async for _ in awatch(filepath):
            messages = await reader.get_new_messages()
            if messages:
                yield messages
    except Exception as e:
        logger.error(f"Watch error: {e}")


# TRUE 95/5: Also export the simple function at module level
async def watch_jsonl(
    filepath: Path | str,
) -> AsyncGenerator[List[Dict[str, Any]], None]:
    """
    Even simpler API - just watch a JSONL file.

    Example:
        async for new_messages in watch_jsonl("session.jsonl"):
            print(f"Got {len(new_messages)} new messages")
    """
    async for messages in stream_jsonl_incrementally(filepath, watch=True):
        yield messages
