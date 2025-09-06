"""
MessageType enum for backward compatibility.

SOLID: Single responsibility - type definitions only
DDD: Value object for message types
Framework: Standard enum for type safety
"""

from enum import Enum


class MessageType(Enum):
    """Message types for Claude conversation parsing."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    SUMMARY = "summary"
