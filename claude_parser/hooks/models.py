#!/usr/bin/env python3
"""
Hook Models - 100% Typer Framework Delegation
LNCA compliant: <80 LOC, single responsibility (data models only)
"""

import typer
from enum import Enum
from typing import Optional

class HookEvent(str, Enum):
    """Type-safe hook events - Typer handles validation"""
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse" 
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    NOTIFICATION = "Notification"
    STOP = "Stop"
    SUBAGENT_STOP = "SubagentStop"
    PRE_COMPACT = "PreCompact"
    SESSION_START = "SessionStart"
    SESSION_END = "SessionEnd"

def allow():
    """Allow operation - Typer handles exit codes"""
    typer.echo("✅ Allowed")
    # Normal exit (0) - Typer handles this

def block(reason: str):
    """Block operation with reason - Typer handles Rich output & exit codes"""
    typer.echo(reason, err=True)
    raise typer.Exit(2)  # Anthropic blocking exit code

def parse_hook_context(
    hook_event_name: HookEvent,
    session_id: str,
    transcript_path: str,
    cwd: str,
    tool_name: Optional[str] = None,
    tool_input: Optional[str] = None,
    tool_response: Optional[str] = None,
    prompt: Optional[str] = None,
    message: Optional[str] = None,
    source: Optional[str] = None,
    stop_hook_active: Optional[bool] = None,
    trigger: Optional[str] = None,
    custom_instructions: Optional[str] = None,
    reason: Optional[str] = None,
) -> dict:
    """Parse hook context - Typer handles type validation"""
    return {
        "hook_event_name": hook_event_name,
        "session_id": session_id,
        "transcript_path": transcript_path,
        "cwd": cwd,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_response": tool_response,
        "prompt": prompt,
        "message": message,
        "source": source,
        "stop_hook_active": stop_hook_active,
        "trigger": trigger,
        "custom_instructions": custom_instructions,
        "reason": reason,
    }