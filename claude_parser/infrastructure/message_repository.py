"""
Simple message repository using msgspec directly.
"""

from pathlib import Path
from typing import List

import msgspec

from ..domain.interfaces.protocols import MessageRepository
from ..domain.value_objects.metadata import ConversationMetadata
from ..models import Message


class JsonlMessageRepository(MessageRepository):
    """Repository for loading messages from JSONL files using msgspec directly."""

    def load_messages(self, filepath: Path) -> List[Message]:
        """Load and validate messages from JSONL file using pure msgspec pattern."""
        messages = []

        with open(filepath, "rb") as f:
            for line in f:
                try:
                    # msgspec handles parsing + validation in one step
                    message = msgspec.json.decode(line, type=Message)
                    messages.append(message)
                except msgspec.DecodeError:
                    # Skip invalid lines, msgspec handles errors natively
                    continue

        return messages

    def get_metadata(self, messages: List[Message], filepath: Path) -> ConversationMetadata:
        """Extract metadata from messages and filepath."""
        session_id = messages[0].session_id if messages else None
        current_dir = messages[0].cwd if messages else None
        git_branch = messages[0].git_branch if messages else None

        return ConversationMetadata(
            session_id=session_id,
            filepath=filepath,
            current_dir=current_dir,
            git_branch=git_branch,
            message_count=len(messages),
            error_count=0,
        )
