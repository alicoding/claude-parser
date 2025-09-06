"""
Tool message models.

SOLID: Single Responsibility - Tool messages only
DDD: Value objects for tool use and results
"""

from typing import Optional, Any, Union, Dict
from pydantic import Field

from .base import BaseMessage, MessageType


class ToolUseMessage(BaseMessage):
    """Tool use message - when Claude calls a tool."""

    type: MessageType = MessageType.TOOL_USE
    name: Optional[str] = Field(None, description="Tool name")
    tool_use_id: Optional[str] = Field(None, alias="toolUseID", description="Tool use identifier")
    input: Optional[Dict[str, Any]] = Field(None, description="Tool input parameters")

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        parts = []
        if self.name:
            parts.append(f"Tool: {self.name}")
        if self.input:
            parts.append(str(self.input))
        return " ".join(parts)


class ToolResultMessage(BaseMessage):
    """Tool result message - response from tool execution."""

    type: MessageType = MessageType.TOOL_RESULT
    tool_use_id: Optional[str] = Field(None, alias="toolUseID", description="Links to tool use")
    tool_use_result: Optional[Union[str, Dict[str, Any]]] = Field(
        None,
        alias="toolUseResult",
        description="Tool execution result"
    )
    is_error: Optional[bool] = Field(None, alias="isError", description="True if tool execution failed")

    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        if isinstance(self.tool_use_result, str):
            return self.tool_use_result
        elif isinstance(self.tool_use_result, dict):
            return str(self.tool_use_result)
        return ""
