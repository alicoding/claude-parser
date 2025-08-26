"""
Message parser utilities.

SOLID: Single Responsibility - Message parsing only
95/5: Using pydantic for validation, orjson for parsing
"""

from typing import Any, Dict, Optional, Union

import orjson
from toolz import filter as toolz_filter
from toolz import map as toolz_map
from toolz import merge, pipe

from ..infrastructure.logger_config import logger
from .assistant import AssistantMessage
from .base import Message, MessageType
from .summary import Summary
from .system import SystemMessage
from .tool import ToolResultMessage, ToolUseMessage
from .user import UserMessage

# Message type mapping
MESSAGE_CLASSES = {
    MessageType.USER: UserMessage,
    MessageType.ASSISTANT: AssistantMessage,
    MessageType.SUMMARY: Summary,
    MessageType.SYSTEM: SystemMessage,
    MessageType.TOOL_USE: ToolUseMessage,
    MessageType.TOOL_RESULT: ToolResultMessage,
}


def parse_message(data: Union[str, bytes, Dict[str, Any]]) -> Optional[Message]:
    """
    Parse a message from various formats.

    LIBRARY FIRST: Using orjson for parsing, pydantic for validation.
    Handles both old format (content at top level) and new format (nested in message field).
    """
    try:
        # Parse JSON if needed
        if isinstance(data, (str, bytes)):
            data = orjson.loads(data)

        # Get message type
        msg_type = data.get("type")
        if not msg_type:
            logger.warning("Message missing type field")
            return None

        # Convert string to enum
        try:
            msg_type_enum = MessageType(msg_type)
        except ValueError:
            logger.warning(f"Unknown message type: {msg_type}")
            return None

        # Get appropriate class
        message_class = MESSAGE_CLASSES.get(msg_type_enum)
        if not message_class:
            logger.warning(f"No class for message type: {msg_type_enum}")
            return None

        # Handle nested message structure (real Claude JSONL format)
        message_data = data.copy()
        if "message" in data and isinstance(data["message"], dict):
            # Extract content from nested message field
            nested_msg = data["message"]
            if "content" in nested_msg:
                content = nested_msg["content"]

                # Handle content as array (for all message types in real Claude format)
                if isinstance(content, list):
                    # Extract text from content blocks using functional approach
                    def extract_text(block):
                        """Extract text from a content block."""
                        if not isinstance(block, dict):
                            return None

                        block_type = block.get("type")
                        if block_type == "text":
                            return block.get("text", "")
                        elif block_type == "tool_result":
                            result_content = block.get("content", "")
                            return (
                                f"[Tool Result] {result_content}"
                                if result_content
                                else None
                            )
                        elif block_type == "tool_use":
                            tool_name = block.get("name", "unknown")
                            return f"[Tool Use: {tool_name}]"
                        return None

                    # Use functional pipeline to extract and join text
                    message_data["content"] = pipe(
                        content,
                        lambda blocks: toolz_map(extract_text, blocks),
                        lambda texts: toolz_filter(lambda x: x is not None, texts),
                        lambda texts: "\n".join(texts),
                    )
                else:
                    # Content is already a string
                    message_data["content"] = content

            # Copy other fields from nested message using functional approach
            fields_to_copy = pipe(
                ["role", "id", "model", "usage"],
                lambda fields: toolz_map(lambda f: (f, nested_msg.get(f)), fields),
                lambda pairs: toolz_filter(lambda p: p[1] is not None, pairs),
                dict,  # Convert to dict
            )
            message_data = merge(message_data, fields_to_copy)

        # Create message instance
        return message_class(**message_data)

    except Exception as e:
        logger.error(f"Failed to parse message: {e}")
        return None
