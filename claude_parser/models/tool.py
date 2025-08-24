"""
Tool-related message models.

SOLID: Single Responsibility - Tool messages only
DDD: Value objects for tool interactions
"""

from typing import Optional, Any, Dict, List, Union
from pydantic import Field
import orjson

from .base import BaseMessage, MessageType


class ToolUse(BaseMessage):
    """Tool use request from assistant.
    
    Represents when Claude invokes a tool like Read, Write, Bash, etc.
    Each tool use has a unique ID to correlate with its result.
    """
    
    type: MessageType = MessageType.TOOL_USE
    tool_use_id: str = Field(
        ...,
        alias="toolUseID",
        description="Unique ID to match this tool use with its result"
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Tool name (e.g., Read, Write, Bash, WebSearch)"
    )
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool-specific parameters passed to the tool"
    )
    
    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        params_str = orjson.dumps(self.parameters).decode() if self.parameters else ""
        return f"Tool: {self.name} {params_str}"
    
    @property
    def tool_name(self) -> str:
        """Alias for consistency."""
        return self.name


class ToolResult(BaseMessage):
    """Result from tool execution.
    
    Contains the output from a tool invocation, either success or error.
    Correlated to ToolUse via tool_use_id.
    """
    
    type: MessageType = MessageType.TOOL_RESULT
    tool_use_id: str = Field(
        ...,
        alias="toolUseID",
        description="Matches the tool_use_id from the corresponding ToolUse"
    )
    tool_name: Optional[str] = Field(
        None,
        alias="toolName",
        description="Name of the tool that was executed"
    )
    
    tool_result: Optional[Union[str, Dict[str, Any], List[Dict[str, Any]]]] = Field(
        None,
        alias="toolUseResult",
        description="Success output: string for simple results, dict/list for structured data"
    )
    
    tool_error: Optional[str] = Field(
        None,
        alias="toolError",
        description="Error message if tool execution failed"
    )
    is_error: Optional[bool] = Field(
        None,
        alias="isError",
        description="True if this represents an error result"
    )
    
    @property
    def text_content(self) -> str:
        """Get searchable text content."""
        if self.tool_error:
            return f"Tool Error: {self.tool_error}"
        elif isinstance(self.tool_result, str):
            return f"Tool Result: {self.tool_result}"
        elif self.tool_result:
            result_str = orjson.dumps(self.tool_result).decode()
            return f"Tool Result: {result_str}"
        return "Tool Result: No output"
    
    @property
    def was_successful(self) -> bool:
        """Check if tool execution succeeded."""
        return not self.is_error and self.tool_error is None