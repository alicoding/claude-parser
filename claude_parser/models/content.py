"""
Content block models for Claude messages.

Based on analysis of 41,085 real messages showing tool_use/tool_result
are CONTENT BLOCKS, not message types.

SOLID: Single responsibility for content block structures
"""

from enum import Enum
from typing import Union, Any, Dict, Optional
from pydantic import BaseModel, Field


class ContentBlockType(str, Enum):
    """Content block types discovered from real messages.

    Distribution from 41,085 messages:
    - text: 12,285 occurrences
    - tool_use: 9,102 occurrences
    - tool_result: 9,102 occurrences
    - thinking: 508 occurrences
    - image: 16 occurrences
    """
    TEXT = "text"
    TOOL_USE = "tool_use"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"
    IMAGE = "image"


class BaseContentBlock(BaseModel):
    """Base class for all content blocks."""

    type: ContentBlockType = Field(
        description="Content block type"
    )


class TextContent(BaseContentBlock):
    """Text content block."""

    type: ContentBlockType = Field(default=ContentBlockType.TEXT)
    text: str = Field(
        description="The text content"
    )


class ThinkingContent(BaseContentBlock):
    """Claude's thinking process content block."""

    type: ContentBlockType = Field(default=ContentBlockType.THINKING)
    content: str = Field(
        description="Claude's internal thinking process"
    )


class ImageContent(BaseContentBlock):
    """Image content block."""

    type: ContentBlockType = Field(default=ContentBlockType.IMAGE)
    source: Dict[str, Any] = Field(
        description="Image source information"
    )


class ToolUseContent(BaseContentBlock):
    """Tool use request content block."""

    type: ContentBlockType = Field(default=ContentBlockType.TOOL_USE)
    id: str = Field(
        description="Tool use ID for linking to result"
    )
    name: str = Field(
        description="Tool name (e.g., 'Bash', 'Edit', 'mcp__desktop-commander__read_file')"
    )
    input: Dict[str, Any] = Field(
        description="Tool input parameters"
    )


class ToolResultContent(BaseContentBlock):
    """Tool execution result content block."""

    type: ContentBlockType = Field(default=ContentBlockType.TOOL_RESULT)
    tool_use_id: str = Field(
        description="ID linking back to tool use request"
    )
    content: Union[str, list] = Field(
        description="Tool execution output"
    )
    is_error: Optional[bool] = Field(
        None,
        description="True if tool execution failed"
    )


# Union type for all content blocks
ContentBlock = Union[
    TextContent,
    ThinkingContent,
    ImageContent,
    ToolUseContent,
    ToolResultContent
]
