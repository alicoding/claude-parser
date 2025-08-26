"""
Async watcher implementation - Watch Domain.

SOLID Principles:
- SRP: Single responsibility - async file watching
- OCP: Open for extension via callbacks
- LSP: Can substitute for sync watcher interface
- ISP: Focused interface - watch_async only
- DIP: Depends on abstractions (watchfiles library)

95/5 Principle:
- Uses watchfiles.awatch (NOT custom file polling)
- Simple async generator interface
- No manual threading (watchfiles handles it)
- TRUE 95/5: Now uses incremental streaming for large files
"""

import asyncio
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional

from loguru import logger
from watchfiles import awatch

from ..domain.entities.conversation import Conversation
from ..infrastructure.message_repository import JsonlMessageRepository
from ..models import Message
from ..models.parser import parse_message
from .true_streaming import StreamingJSONLReader


class AsyncWatcher:
    """Async file watcher following DDD principles."""

    def __init__(self, repository: Optional[JsonlMessageRepository] = None):
        """Initialize with repository dependency injection."""
        self._repository = repository or JsonlMessageRepository()
        self._streaming_reader: Optional[StreamingJSONLReader] = None
        self._all_messages: List[Dict[str, Any]] = []

    async def watch_async(
        self,
        file_path: str | Path,
        message_types: Optional[List[str]] = None,
        debounce: int = 100,
        stop_event: Optional[asyncio.Event] = None,
    ) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
        """
        Asynchronously watch a JSONL file for changes.

        Uses watchfiles.awatch internally - NO manual threading!
        The Rust backend runs in a separate thread automatically.

        Args:
            file_path: Path to JSONL file
            message_types: Optional filter for message types
            debounce: Milliseconds to debounce rapid changes
            stop_event: Optional event to stop watching

        Yields:
            Tuple of (full_conversation, new_messages)
        """
        file_path = Path(file_path)

        # Wait for file creation if needed
        if not file_path.exists():
            logger.info(f"Waiting for {file_path.name} to be created...")
            async for changes in awatch(str(file_path.parent), stop_event=stop_event):
                if any(str(file_path) in path for _, path in changes):
                    break

        # Initialize streaming reader
        self._streaming_reader = StreamingJSONLReader(file_path)
        self._all_messages = []

        # Initial load using TRUE streaming
        if file_path.exists():
            logger.debug(f"Initial load for {file_path}")
            result = await self._process_file_incremental(
                file_path, message_types, initial=True
            )
            if result:
                logger.debug(f"Initial load yielded {len(result[1])} messages")
                yield result
            else:
                logger.debug("Initial load returned no results")

        # Watch for changes - awatch handles threading!
        logger.info(f"Watching {file_path.name} asynchronously...")

        async for changes in awatch(
            str(file_path), debounce=debounce, stop_event=stop_event
        ):
            # Process any changes (not just modifications)
            logger.debug(f"Detected changes: {changes}")
            for change_type, path in changes:
                logger.debug(f"Change type: {change_type}, path: {path}")
                # Process on any change (modified, added, etc)
                result = await self._process_file_incremental(file_path, message_types)
                if result:
                    logger.debug(f"Yielding {len(result[1])} new messages")
                    yield result
                    break  # Only process once per change set

    async def _process_file_incremental(
        self,
        file_path: Path,
        message_types: Optional[List[str]] = None,
        initial: bool = False,
    ) -> Optional[tuple[Conversation, List[Message]]]:
        """Process file changes incrementally using TRUE streaming."""
        try:
            # Get new raw messages using TRUE streaming
            new_raw_messages = await self._streaming_reader.get_new_messages()
            logger.debug(
                f"Got {len(new_raw_messages) if new_raw_messages else 0} raw messages"
            )

            if not new_raw_messages:
                logger.debug("No new raw messages, returning None")
                return None

            # Add to our complete list
            self._all_messages.extend(new_raw_messages)

            # Convert raw messages to Message objects
            new_messages = []
            for raw_msg in new_raw_messages:
                try:
                    # Parse using the parse_message function
                    msg = parse_message(raw_msg)
                    if msg:
                        # Handle list case (embedded tools)
                        if isinstance(msg, list):
                            for m in msg:
                                if not message_types or m.type.value in message_types:
                                    new_messages.append(m)
                        else:
                            if not message_types or msg.type.value in message_types:
                                new_messages.append(msg)
                except Exception as e:
                    logger.warning(f"Failed to parse message: {e}")

            if new_messages:
                # Parse all messages for complete conversation
                all_parsed_messages = []
                for raw_msg in self._all_messages:
                    try:
                        msg = parse_message(raw_msg)
                        if msg:
                            if isinstance(msg, list):
                                all_parsed_messages.extend(msg)
                            else:
                                all_parsed_messages.append(msg)
                    except Exception:
                        pass

                # Create conversation with all messages
                metadata = self._repository.get_metadata_from_messages(
                    all_parsed_messages, file_path
                )
                conv = Conversation(all_parsed_messages, metadata)

                return conv, new_messages

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return None

    # Keep old method for compatibility but deprecated
    async def _process_file(
        self,
        file_path: Path,
        message_types: Optional[List[str]] = None,
        initial: bool = False,
    ) -> Optional[tuple[Conversation, List[Message]]]:
        """DEPRECATED: Old method kept for compatibility."""
        return await self._process_file_incremental(file_path, message_types, initial)


# ==========================================
# 95/5 FACTORY FUNCTION (Main API)
# ==========================================


async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
    """
    Watch a JSONL file asynchronously for changes.

    95/5 Principle: Dead simple async API - no threading needed!
    Uses watchfiles which runs Rust code in a separate thread.

    Args:
        file_path: Path to JSONL file
        message_types: Optional filter ["user", "assistant", etc]
        stop_event: Optional event to stop watching

    Yields:
        (conversation, new_messages) on each change

    Example:
        async for conv, new_messages in watch_async("session.jsonl"):
            for msg in new_messages:
                print(f"{msg.type}: {msg.text_content}")
    """
    watcher = AsyncWatcher()
    async for result in watcher.watch_async(
        file_path, message_types, stop_event=stop_event
    ):
        yield result
