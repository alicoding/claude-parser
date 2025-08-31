"""Watch domain implementation following 95/5 principle.

Single Responsibility: File watching with UUID-based checkpoint tracking.
Uses watchfiles library for cross-platform file monitoring.
Uses native Anthropic UUID system - no byte position tracking.
"""

import sys
from pathlib import Path
from typing import Callable, List, Optional, Set

from more_itertools import consume
from toolz import filter as toolz_filter
from toolz import map as toolz_map

try:
    import watchfiles
except ImportError:
    print(
        "watchfiles library required. Install with: pip install watchfiles",
        file=sys.stderr,
    )
    sys.exit(1)

from .. import load
from ..domain.entities.conversation import Conversation
from ..models.base import Message
from .uuid_tracker import UUIDCheckpointReader


class UUIDBasedReader:
    """Single Responsibility: Track messages using native UUID checkpoints."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.reader = UUIDCheckpointReader(file_path)
        self.last_inode = None

    def get_new_messages(self, after_uuid: Optional[str] = None) -> List[dict]:
        """Get new messages after UUID checkpoint."""
        try:
            stat = self.file_path.stat()
            current_inode = stat.st_ino

            # Handle file rotation (inode changed)
            if self.last_inode is not None and current_inode != self.last_inode:
                self.reader.reset()  # Reset on rotation

            self.last_inode = current_inode

            # Get new messages using UUID tracking
            import asyncio

            loop = asyncio.new_event_loop()
            try:
                messages = loop.run_until_complete(
                    self.reader.get_new_messages(after_uuid)
                )
                return messages
            finally:
                loop.close()

        except (FileNotFoundError, PermissionError):
            return []


def watch(
    file_path: str,
    callback: Callable[[Conversation, List[Message]], None],
    message_types: Optional[List[str]] = None,
    after_uuid: Optional[str] = None,
) -> None:
    """
    Watch JSONL file for changes and call callback with new messages.

    Args:
        file_path: Path to JSONL file
        callback: Function called with (full_conversation, new_messages)
        message_types: Optional filter ["user", "assistant", "tool_use", etc.]
        after_uuid: Optional UUID to resume after (for checkpoint recovery)

    Example (95% use case):
        def on_new(conv, new_msgs):
            print(f"Got {len(new_msgs)} new messages")
            # Client can track: last_uuid = new_msgs[-1].uuid

        watch("session.jsonl", on_new)  # Blocks, monitors forever

        # Or resume from checkpoint:
        watch("session.jsonl", on_new, after_uuid="abc-123")
    """
    file_path = str(Path(file_path).resolve())

    # Verify file exists
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    reader = UUIDBasedReader(file_path)
    message_type_filter: Optional[Set[str]] = (
        set(message_types) if message_types else None
    )

    # If after_uuid provided, set checkpoint
    if after_uuid:
        reader.reader.set_checkpoint(after_uuid)
    else:
        # Process initial file state (skip existing content)
        initial_messages = reader.get_new_messages()
        # Mark all as processed without callback
        if initial_messages:
            for msg in initial_messages:
                if uuid := msg.get("uuid"):
                    reader.reader.processed_uuids.add(uuid)
                    reader.reader.last_uuid = uuid

    # Define processing function for each change set
    from functools import partial

    process_fn = partial(
        _process_file_changes,
        file_path=file_path,
        reader=reader,
        message_type_filter=message_type_filter,
        callback=callback,
    )

    try:
        # Consume infinite generator functionally using more_itertools.consume
        # This replaces the for loop with functional approach
        consume(toolz_map(process_fn, watchfiles.watch(file_path)))

    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        pass
    except Exception as e:
        print(f"Watch error: {e}", file=sys.stderr)
        raise


def _process_file_changes(
    changes, file_path: str, reader, message_type_filter, callback
):
    """Process file changes functionally using UUID tracking."""
    # Filter changes to only our target file
    relevant_changes = toolz_filter(lambda change: change[1] == file_path, changes)

    # Process if we have relevant changes
    if any(relevant_changes):
        raw_messages = reader.get_new_messages()

        if raw_messages:
            new_messages = _parse_new_messages_from_dicts(
                raw_messages, message_type_filter
            )

            if new_messages:
                full_conversation = load(file_path)
                callback(full_conversation, new_messages)


def _parse_new_messages_from_dicts(
    raw_messages: List[dict], message_type_filter: Optional[Set[str]]
) -> List[Message]:
    """Parse raw message dicts into Message objects."""
    from ..models import parse_message

    def parse_dict_safe(raw_data):
        """Parse a dict safely, return message or None."""
        try:
            message = parse_message(raw_data)

            # Apply message type filter if specified
            if message_type_filter is None or message.type in message_type_filter:
                return message
            return None

        except Exception as e:
            # Log parsing error but don't crash watcher
            print(f"Failed to parse message: {e}", file=sys.stderr)
            return None

    # Use functional approach instead of manual loops
    parsed_messages = toolz_map(parse_dict_safe, raw_messages)
    valid_messages = toolz_filter(lambda msg: msg is not None, parsed_messages)

    return list(valid_messages)
