"""
Polars + msgspec implementation of data processing interfaces.

SINGLE PLACE for framework dependencies - all polars/msgspec usage centralized here.
When we change frameworks, we only change this file.

DIP: Implements domain interfaces, doesn't export framework details.
SRP: Each class has single responsibility for one type of operation.
"""

from pathlib import Path
from typing import List, Optional

import msgspec
import polars as pl

from ...domain.entities.conversation import Conversation
from ...domain.interfaces.data_processor import MessageParser, MessageFilter, ConversationBuilder, DataProcessor
from ...domain.value_objects.metadata import ConversationMetadata
from ...models import Message


class PolarsMessageParser(MessageParser):
    """Parse messages using Polars for efficient JSONL processing."""

    def parse_jsonl_file(self, file_path: Path) -> List[Message]:
        """Parse JSONL file using Polars streaming + msgspec validation."""
        try:
            # Use Polars streaming for efficient file reading
            df = pl.scan_ndjson(file_path).collect()

            # Convert to Message objects using msgspec
            messages = []
            for row in df.iter_rows(named=True):
                try:
                    # msgspec handles JSON dict → Message conversion
                    message = msgspec.convert(row, Message)
                    messages.append(message)
                except msgspec.ValidationError:
                    # Skip invalid messages - framework handles errors
                    continue

            return messages

        except Exception:
            # Fallback: read line by line if Polars fails
            return self._parse_fallback(file_path)

    def parse_jsonl_content(self, content: str) -> List[Message]:
        """Parse JSONL content string using msgspec."""
        messages = []
        for line in content.strip().split('\n'):
            if not line.strip():
                continue
            try:
                message = msgspec.json.decode(line.encode(), type=Message)
                messages.append(message)
            except msgspec.DecodeError:
                continue
        return messages

    def _parse_fallback(self, file_path: Path) -> List[Message]:
        """Fallback parser using direct file reading + msgspec."""
        messages = []
        with open(file_path, 'rb') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    message = msgspec.json.decode(line, type=Message)
                    messages.append(message)
                except msgspec.DecodeError:
                    continue
        return messages


class PolarsMessageFilter(MessageFilter):
    """Filter messages using Polars DataFrame operations."""

    def filter_by_types(self, messages: List[Message], types: List[str]) -> List[Message]:
        """Filter messages by type using Polars."""
        if not messages:
            return []

        # Convert to DataFrame for efficient filtering
        df = pl.DataFrame([
            {"message": msg, "type": msg.type.value}
            for msg in messages
        ])

        # Use Polars filtering
        filtered_df = df.filter(pl.col("type").is_in(types))

        return [row["message"] for row in filtered_df.iter_rows(named=True)]

    def filter_after_uuid(self, messages: List[Message], after_uuid: str) -> List[Message]:
        """Get messages after UUID using efficient search."""
        for i, message in enumerate(messages):
            if message.uuid == after_uuid:
                return messages[i + 1:]
        return messages  # UUID not found, return all

    def find_new_messages(self, old_messages: List[Message], new_messages: List[Message]) -> List[Message]:
        """Find new messages using length comparison."""
        if len(new_messages) <= len(old_messages):
            return []
        return new_messages[len(old_messages):]


class PolarsConversationBuilder(ConversationBuilder):
    """Build conversations with metadata generation."""

    def build_conversation(self, messages: List[Message], file_path: Path) -> Conversation:
        """Build conversation with auto-generated metadata."""
        if not messages:
            metadata = ConversationMetadata(
                session_id=None,
                filepath=file_path,
                current_dir="",
                git_branch="",
                message_count=0,
                error_count=0,
            )
        else:
            first_message = messages[0]
            metadata = ConversationMetadata(
                session_id=first_message.session_id,
                filepath=file_path,
                current_dir=getattr(first_message, 'cwd', ''),
                git_branch=getattr(first_message, 'git_branch', ''),
                message_count=len(messages),
                error_count=0,
            )

        return Conversation(messages, metadata)


class PolarsDataProcessor(DataProcessor):
    """Combined data processor using Polars + msgspec."""

    def __init__(self):
        self._parser = PolarsMessageParser()
        self._filter = PolarsMessageFilter()
        self._builder = PolarsConversationBuilder()

    @property
    def parser(self) -> MessageParser:
        return self._parser

    @property
    def filter(self) -> MessageFilter:
        return self._filter

    @property
    def builder(self) -> ConversationBuilder:
        return self._builder


# Factory function - 95/5 principle
def create_data_processor() -> DataProcessor:
    """Create a data processor using best available frameworks."""
    return PolarsDataProcessor()
