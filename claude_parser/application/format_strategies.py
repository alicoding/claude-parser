"""
Format strategies for streaming service.

SOLID: Open/Closed Principle - Add new formats without modifying existing code.
Strategy Pattern: Each format has its own strategy class.
95/5: Part of the 5% glue code.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, List

import msgspec


class FormatStrategy(ABC):
    """Abstract base class for format strategies."""

    @abstractmethod
    def format_message(self, message: Dict[str, Any]) -> str:
        """Format a single message."""
        pass

    @abstractmethod
    def format_batch(self, messages: List[Dict[str, Any]]) -> str:
        """Format a batch of messages."""
        pass

    @abstractmethod
    def get_content_type(self) -> str:
        """Get the content type for this format."""
        pass


class PlainTextFormatStrategy(FormatStrategy):
    """Plain text format strategy."""

    def format_message(self, message: Dict[str, Any]) -> str:
        """Format message as plain text."""
        return f"{message}\n"

    def format_batch(self, messages: List[Dict[str, Any]]) -> str:
        """Format batch as plain text."""
        return "\n".join(str(msg) for msg in messages)

    def get_content_type(self) -> str:
        """Return plain text content type."""
        return "text/plain"


class JSONFormatStrategy(FormatStrategy):
    """JSON format strategy."""

    def format_message(self, message: Dict[str, Any]) -> str:
        """Format message as JSON."""
        return msgspec.json.encode(message).decode()

    def format_batch(self, messages: List[Dict[str, Any]]) -> str:
        """Format batch as JSON array."""
        return msgspec.json.encode(messages).decode()

    def get_content_type(self) -> str:
        """Return JSON content type."""
        return "application/json"


class SSEFormatStrategy(FormatStrategy):
    """Server-Sent Events format strategy."""

    def format_message(self, message: Dict[str, Any]) -> str:
        """Format message as SSE."""
        json_str = self._exporter.serialize_data(message)
        return f"data: {json_str}\n\n"

    def format_batch(self, messages: List[Dict[str, Any]]) -> str:
        """Format batch as SSE stream."""
        return "".join(self.format_message(msg) for msg in messages)

    def get_content_type(self) -> str:
        """Return SSE content type."""
        return "text/event-stream"


class NDJSONFormatStrategy(FormatStrategy):
    """Newline-delimited JSON format strategy."""

    def format_message(self, message: Dict[str, Any]) -> str:
        """Format message as NDJSON."""
        return self._exporter.serialize_data(message) + "\n"

    def format_batch(self, messages: List[Dict[str, Any]]) -> str:
        """Format batch as NDJSON."""
        return "".join(self.format_message(msg) for msg in messages)

    def get_content_type(self) -> str:
        """Return NDJSON content type."""
        return "application/x-ndjson"


class FormatStrategyFactory:
    """Factory for creating format strategies."""

    _strategies = {
        "plain": PlainTextFormatStrategy,
        "json": JSONFormatStrategy,
        "sse": SSEFormatStrategy,
        "ndjson": NDJSONFormatStrategy,
    }

    @classmethod
    def create(cls, format_name: str) -> FormatStrategy:
        """Create a format strategy by name."""
        strategy_class = cls._strategies.get(format_name.lower())
        if not strategy_class:
            raise ValueError(f"Unknown format: {format_name}")
        return strategy_class()

    @classmethod
    def register(cls, name: str, strategy_class: type):
        """Register a new format strategy."""
        cls._strategies[name.lower()] = strategy_class


# Export for convenience
__all__ = [
    'FormatStrategy',
    'PlainTextFormatStrategy',
    'JSONFormatStrategy',
    'SSEFormatStrategy',
    'NDJSONFormatStrategy',
    'FormatStrategyFactory',
]
