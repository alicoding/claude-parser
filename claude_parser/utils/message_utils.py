"""
Message utility functions to eliminate duplication.

SOLID: Single Responsibility - Message inspection utilities.
DRY: Eliminate repeated message checking patterns.
95/5: Using toolz for functional operations.
"""

from typing import Any, Dict, List, Optional
from toolz import get_in


def has_content_blocks(msg: Any) -> bool:
    """Check if message has content_blocks attribute."""
    return hasattr(msg, "content_blocks") and msg.content_blocks is not None


def has_message_dict(msg: Any) -> bool:
    """Check if message has a message attribute that is a dict."""
    return hasattr(msg, "message") and isinstance(msg.message, dict)


def get_message_content(msg: Any) -> Optional[List[Dict]]:
    """
    Get content from message dict safely.

    Returns the content array from message.message.content if it exists.
    """
    if not has_message_dict(msg):
        return None

    # Use toolz.get_in for safe nested access
    return get_in(["content"], msg.message, default=None)


def get_content_blocks(msg: Any) -> List:
    """
    Get content blocks from message safely.

    Returns content_blocks if they exist, otherwise checks message.content.
    """
    if has_content_blocks(msg):
        return msg.content_blocks

    content = get_message_content(msg)
    return content if content else []


def extract_text_from_content(content: List[Dict]) -> str:
    """
    Extract text from content blocks.

    Handles both text blocks and other content types.
    """
    if not content:
        return ""

    # Use functional approach with toolz
    from toolz import pipe, filter as toolz_filter, map as toolz_map

    def get_text(block):
        if isinstance(block, dict):
            if block.get("type") == "text":
                return block.get("text", "")
            elif "text" in block:
                return block["text"]
        return ""

    return " ".join(
        pipe(
            content,
            toolz_map(get_text),
            toolz_filter(lambda x: x),  # Filter out empty strings
        )
    )


def extract_tool_blocks(content: List[Dict]) -> List[Dict]:
    """
    Extract tool-related blocks from content.

    Returns blocks with type 'tool_use' or 'tool_result'.
    """
    if not content:
        return []

    # Use functional approach with toolz
    from toolz import filter as toolz_filter

    return list(
        toolz_filter(
            lambda block: (
                isinstance(block, dict)
                and block.get("type", "") in ["tool_use", "tool_result"]
            ),
            content,
        )
    )


def get_message_usage(msg: Any) -> Optional[Dict]:
    """
    Get usage data from message safely.

    Checks both direct usage attribute and message.usage.
    """
    # Check direct attribute
    if hasattr(msg, "usage") and msg.usage:
        return msg.usage

    # Check in message dict
    if has_message_dict(msg):
        return get_in(["usage"], msg.message, default=None)

    return None


def get_message_model(msg: Any) -> Optional[str]:
    """
    Get model name from message safely.

    Checks multiple possible locations.
    """
    # Check direct attribute
    if hasattr(msg, "model") and msg.model:
        return msg.model

    # Check in message dict
    if has_message_dict(msg):
        model = get_in(["model"], msg.message)
        if model:
            return model

    # Check raw_data
    if hasattr(msg, "raw_data") and isinstance(msg.raw_data, dict):
        return msg.raw_data.get("model")

    return None


def is_compact_summary(msg: Any) -> bool:
    """Check if message is a compact summary."""
    if hasattr(msg, "raw_data") and isinstance(msg.raw_data, dict):
        return msg.raw_data.get("isCompactSummary", False)
    return False


def get_session_id(msg: Any) -> Optional[str]:
    """
    Get session ID from message safely.

    Checks multiple possible locations.
    """
    # Direct attribute
    if hasattr(msg, "session_id"):
        return msg.session_id

    # In raw_data
    if hasattr(msg, "raw_data") and isinstance(msg.raw_data, dict):
        return msg.raw_data.get("sessionId") or msg.raw_data.get("session_id")

    return None


# Export all utilities
__all__ = [
    "has_content_blocks",
    "has_message_dict",
    "get_message_content",
    "get_content_blocks",
    "extract_text_from_content",
    "extract_tool_blocks",
    "get_message_usage",
    "get_message_model",
    "is_compact_summary",
    "get_session_id",
]
