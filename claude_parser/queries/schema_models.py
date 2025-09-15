#!/usr/bin/env python3
"""
Schema models - @FRAMEWORK_FIRST Pydantic models for JSONL normalization.
@SINGLE_SOURCE_TRUTH: All JSONL schema definitions HERE.
"""
from typing import Optional
from pydantic import BaseModel, Field, validator


class ToolUseResult(BaseModel):
    """@FRAMEWORK_FIRST: Pydantic model for toolUseResult normalization."""
    type: Optional[str] = None
    filePath: Optional[str] = Field(None, alias='file_path')
    content: Optional[str] = None

    @validator('*', pre=True, allow_reuse=True)
    def parse_string_json(cls, v):
        """Handle toolUseResult as string or dict - 100% Pydantic."""
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except:
                return v
        return v


class NormalizedMessage(BaseModel):
    """@FRAMEWORK_FIRST: Pydantic schema for normalized JSONL messages."""
    uuid: str
    timestamp: Optional[str] = None
    type: Optional[str] = None
    tool_result: Optional[ToolUseResult] = Field(None, alias='toolUseResult')

    @validator('tool_result', pre=True, allow_reuse=True)
    def normalize_tool_result(cls, v):
        """Normalize toolUseResult variations using Pydantic."""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                import json
                v = json.loads(v)
            except:
                return None
        return ToolUseResult.parse_obj(v) if isinstance(v, dict) else None

    @property
    def tool_name(self) -> Optional[str]:
        """@FRAMEWORK_FIRST: Delegate to Pydantic model."""
        return self.tool_result.type if self.tool_result else None

    @property
    def file_path(self) -> Optional[str]:
        """@FRAMEWORK_FIRST: Delegate to Pydantic model."""
        return self.tool_result.filePath if self.tool_result else None