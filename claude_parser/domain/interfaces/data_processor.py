"""
Domain interfaces for data processing operations.

SOLID: Interface Segregation - focused, single-responsibility interfaces
DIP: High-level modules depend on these abstractions, not concrete implementations
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Protocol

from ...models import Message
from ..entities.conversation import Conversation


class MessageParser(Protocol):
    """Abstract interface for parsing messages from different sources."""

    def parse_jsonl_file(self, file_path: Path) -> List[Message]:
        """Parse JSONL file and return validated Message objects."""
        ...

    def parse_jsonl_content(self, content: str) -> List[Message]:
        """Parse JSONL content string and return validated Message objects."""
        ...


class MessageFilter(Protocol):
    """Abstract interface for filtering and querying messages."""

    def filter_by_types(self, messages: List[Message], types: List[str]) -> List[Message]:
        """Filter messages by type."""
        ...

    def filter_after_uuid(self, messages: List[Message], after_uuid: str) -> List[Message]:
        """Get messages after a specific UUID."""
        ...

    def find_new_messages(self, old_messages: List[Message], new_messages: List[Message]) -> List[Message]:
        """Find messages that are new compared to previous state."""
        ...


class ConversationBuilder(Protocol):
    """Abstract interface for building conversation objects."""

    def build_conversation(self, messages: List[Message], file_path: Path) -> Conversation:
        """Build a complete conversation object with metadata."""
        ...


class DataProcessor(Protocol):
    """High-level interface combining all data operations."""

    @property
    def parser(self) -> MessageParser:
        """Get the message parser."""
        ...

    @property
    def filter(self) -> MessageFilter:
        """Get the message filter."""
        ...

    @property
    def builder(self) -> ConversationBuilder:
        """Get the conversation builder."""
        ...
