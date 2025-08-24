"""Hook response models using pydantic - replaces 145 lines with ~30."""

import sys
from typing import Optional, Literal
from pydantic import BaseModel, Field
import orjson


class HookResponse(BaseModel):
    """Base hook response that outputs JSON and exits."""
    
    def respond(self) -> None:
        """Output JSON and exit."""
        print(self.model_dump_json())
        sys.exit(0)


from pydantic import Field

class SimpleResponse(HookResponse):
    """Simple continue response for most hooks - matches Claude's expected format."""
    continue_: bool = Field(default=True, alias="continue")  # Use Field with alias


class PreToolUseResponse(HookResponse):
    """PreToolUse specific response."""
    hookSpecificOutput: dict = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": None
    }


class ContextResponse(HookResponse):
    """Response with additional context for UserPromptSubmit/SessionStart."""
    hookSpecificOutput: dict = {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": ""
    }