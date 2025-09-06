"""
UUID-based checkpoint tracking for JSONL streaming.

Following Anthropic's native checkpoint system - every message has a UUID.
No byte position tracking, no reinventing the wheel.

SOLID Principles:
- SRP: Single responsibility - UUID-based message tracking
- OCP: Open for extension via different tracking strategies
- DIP: Depends on abstractions (message UUIDs)
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import orjson
from ..infrastructure.logger_config import logger


class UUIDCheckpointReader:
    """
    Native UUID-based checkpoint reader for JSONL files.

    Uses Anthropic's built-in UUID system instead of byte positions.
    Each message has a unique UUID, perfect for checkpointing.
    """

    def __init__(self, filepath: Path | str):
        """Initialize with filepath only - no position tracking."""
        self.filepath = Path(filepath)
        self.processed_uuids: Set[str] = set()
        self.last_uuid: Optional[str] = None

    def set_checkpoint(self, last_uuid: str) -> None:
        """Set the last processed UUID for resuming."""
        self.last_uuid = last_uuid
        logger.debug(f"Checkpoint set to UUID: {last_uuid}")

    async def get_new_messages(self, after_uuid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages after a specific UUID checkpoint.

        Args:
            after_uuid: UUID to start after (uses self.last_uuid if not provided)

        Returns:
            List of new messages after the checkpoint
        """
        checkpoint = after_uuid or self.last_uuid
        messages = []
        found_checkpoint = checkpoint is None  # If no checkpoint, start from beginning

        if not self.filepath.exists():
            return messages

        try:
            # Read ALL messages (we need to scan for UUID)
            with open(self.filepath, 'rb') as f:
                for line in f:
                    try:
                        data = orjson.loads(line)
                        current_uuid = data.get('uuid')

                        if not current_uuid:
                            continue

                        # Skip if already processed (for deduplication)
                        if current_uuid in self.processed_uuids:
                            continue

                        # If we haven't found checkpoint yet, check if this is it
                        if not found_checkpoint:
                            if current_uuid == checkpoint:
                                found_checkpoint = True
                            continue

                        # We're past the checkpoint, collect this message
                        messages.append(data)
                        self.processed_uuids.add(current_uuid)
                        self.last_uuid = current_uuid

                    except Exception as e:
                        logger.warning(f"Failed to parse line: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading file: {e}")

        return messages

    def get_messages_between(self, start_uuid: Optional[str], end_uuid: Optional[str]) -> List[Dict[str, Any]]:
        """
        Get messages between two UUID checkpoints.

        Useful for replaying specific conversation segments.
        """
        messages = []
        collecting = start_uuid is None  # If no start, collect from beginning

        if not self.filepath.exists():
            return messages

        try:
            with open(self.filepath, 'rb') as f:
                for line in f:
                    try:
                        data = orjson.loads(line)
                        current_uuid = data.get('uuid')

                        if not current_uuid:
                            continue

                        # Start collecting after start_uuid
                        if not collecting and current_uuid == start_uuid:
                            collecting = True
                            continue

                        # Stop at end_uuid
                        if end_uuid and current_uuid == end_uuid:
                            break

                        if collecting:
                            messages.append(data)

                    except Exception as e:
                        logger.warning(f"Failed to parse line: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading file: {e}")

        return messages

    def reset(self) -> None:
        """Reset checkpoint state for fresh reading."""
        self.processed_uuids.clear()
        self.last_uuid = None


class MultiFileUUIDTracker:
    """
    Track UUID checkpoints across multiple JSONL files in a project.

    Perfect for watching entire Claude projects with branching/threading.
    """

    def __init__(self):
        """Initialize multi-file tracker."""
        self.readers: Dict[str, UUIDCheckpointReader] = {}
        self.checkpoints: Dict[str, str] = {}  # filename -> last_uuid

    def set_checkpoints(self, checkpoints: Dict[str, str]) -> None:
        """Set checkpoints for multiple files at once."""
        self.checkpoints = checkpoints
        for filename, uuid in checkpoints.items():
            if filename in self.readers:
                self.readers[filename].set_checkpoint(uuid)

    def get_reader(self, filepath: Path | str) -> UUIDCheckpointReader:
        """Get or create reader for a file."""
        filepath = Path(filepath)
        filename = filepath.name

        if filename not in self.readers:
            self.readers[filename] = UUIDCheckpointReader(filepath)
            # Apply checkpoint if we have one
            if filename in self.checkpoints:
                self.readers[filename].set_checkpoint(self.checkpoints[filename])

        return self.readers[filename]

    async def get_new_messages_for_file(self, filepath: Path | str) -> List[Dict[str, Any]]:
        """Get new messages for a specific file."""
        reader = self.get_reader(filepath)
        return await reader.get_new_messages()

    def get_current_checkpoints(self) -> Dict[str, Optional[str]]:
        """Get current checkpoint UUIDs for all tracked files."""
        return {
            filename: reader.last_uuid
            for filename, reader in self.readers.items()
        }
