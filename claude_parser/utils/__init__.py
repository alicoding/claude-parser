"""
Utility modules for common operations.

SOLID: Utilities have single responsibilities.
DRY: Eliminate duplication across the codebase.
95/5: Part of the 5% glue code.
"""

from .message_utils import (
    has_content_blocks,
    has_message_dict,
    get_message_content,
    get_content_blocks,
    extract_text_from_content,
    extract_tool_blocks,
    get_message_usage,
    get_message_model,
    is_compact_summary,
    get_session_id,
)

__all__ = [
    # Message utilities
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
