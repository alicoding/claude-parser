"""Hook data models for Claude Code hooks.

Following DRY principle: Single model for ALL 8 hook types.
No subclasses, no isinstance checks needed.
"""

from typing import Optional, Dict, Any, Literal, Union, List
from pydantic import BaseModel, Field, ConfigDict

# All 8 Claude Code hook types
HookEventType = Literal[
    "PreToolUse",
    "PostToolUse", 
    "Notification",
    "UserPromptSubmit",
    "Stop",
    "SubagentStop",
    "PreCompact",
    "SessionStart"
]


class HookData(BaseModel):
    """Universal hook data model (DRY principle).
    
    Single model handles ALL 8 Claude Code hook types.
    Immutable value object following DDD principles.
    
    Example:
        data = HookData(**json_from_stdin)
        print(data.hook_type)  # Works for any hook
        print(data.tool_name)  # None if not a tool hook
    """
    
    model_config = ConfigDict(
        frozen=True,  # Immutable (DDD value object pattern)
        extra="allow",  # Forward compatibility with new fields
        populate_by_name=True,  # Accept both snake_case and camelCase
    )
    
    # ===== Required fields (ALL hooks have these) =====
    session_id: str = Field(..., min_length=1, alias="sessionId")
    transcript_path: str = Field(..., min_length=1, alias="transcriptPath")
    cwd: str = Field(..., min_length=1)  # Already snake_case
    hook_event_name: HookEventType = Field(..., alias="hookEventName")
    
    # ===== Tool-specific fields (PreToolUse, PostToolUse) =====
    tool_name: Optional[str] = Field(None, alias="toolName")
    tool_input: Optional[Dict[str, Any]] = Field(None, alias="toolInput")
    # BUG FIX: Accept strings from LS, Grep, Read, Bash tools
    tool_response: Optional[Union[str, Dict[str, Any], List[Dict[str, Any]]]] = Field(None, alias="toolResponse")
    
    # ===== Other hook-specific fields =====
    prompt: Optional[str] = None  # UserPromptSubmit
    message: Optional[str] = None  # Notification
    stop_hook_active: Optional[bool] = None  # Stop, SubagentStop
    trigger: Optional[str] = None  # PreCompact (manual/auto)
    custom_instructions: Optional[str] = None  # PreCompact
    source: Optional[str] = None  # SessionStart (startup/resume/clear)
    
    @property
    def hook_type(self) -> str:
        """Convenience alias for hook_event_name.
        
        Makes code more readable for 95% of users.
        
        Returns:
            The hook event name (e.g., "PreToolUse")
        """
        return self.hook_event_name
    
    def load_conversation(self) -> Any:  # Returns Conversation but avoid circular import
        """Load the conversation from transcript_path.
        
        Integration point with Parser domain (Phase 1).
        Enables hooks to access conversation history.
        
        Returns:
            Conversation object from the transcript file
            
        Example:
            data = hook_input()
            conv = data.load_conversation()
            recent = conv.messages_before_summary(10)
        """
        from claude_parser import load
        return load(self.transcript_path)