#!/usr/bin/env python3
"""
Hook Handlers - 100% Typer Framework Delegation  
LNCA compliant: <80 LOC, single responsibility (business logic only)
"""

import typer
from typing import Optional
from .models import HookEvent, allow, block

def handle_pre_tool_use(tool_name: Optional[str], tool_input: Optional[str]):
    """Pre-tool validation with Rich output via Typer"""
    if not tool_name:
        return allow()
        
    # Security validation
    if tool_input and any(word in tool_input.lower() for word in ["password", "secret", "key", "token"]):
        block("🚫 Security policy violation: Sensitive information detected")
        
    # Tool-specific validation
    if tool_name == "Write" and tool_input and "rm -rf" in tool_input:
        block("🚫 Dangerous file operation blocked")
    
    allow()

def handle_post_tool_use(tool_name: Optional[str], tool_response: Optional[str]):
    """Post-tool analysis with Rich output via Typer"""
    # Could integrate with existing claude-parser analytics
    # For now, simple validation
    allow()

def handle_user_prompt(prompt: Optional[str]):
    """User prompt filtering with Rich output via Typer"""
    if not prompt:
        return allow()
        
    # Enhanced validation could integrate with claude-parser conversation loading
    if len(prompt) > 50000:  # Very large prompts
        typer.echo("⚠️  Large prompt detected - consider breaking into smaller parts", err=False)
    
    allow()

def handle_notification(message: Optional[str]):
    """Notification hook - log and continue"""
    if message:
        typer.echo(f"📢 {message}", err=False)
    allow()

# Simple handlers that just allow - optimized for LOC compliance
handle_stop = lambda _: allow()
handle_subagent_stop = lambda _: allow()
handle_pre_compact = lambda _, __: allow()
handle_session_start = lambda _: allow()
handle_session_end = lambda _: allow()

def route_hook_event(hook_event_name: HookEvent, **kwargs):
    """Route hook events - Typer handles type validation"""
    try:
        # Handler mapping for concise routing
        handlers = {
            HookEvent.PRE_TOOL_USE: lambda: handle_pre_tool_use(kwargs.get("tool_name"), kwargs.get("tool_input")),
            HookEvent.POST_TOOL_USE: lambda: handle_post_tool_use(kwargs.get("tool_name"), kwargs.get("tool_response")),
            HookEvent.USER_PROMPT_SUBMIT: lambda: handle_user_prompt(kwargs.get("prompt")),
            HookEvent.STOP: lambda: handle_stop(kwargs.get("stop_hook_active")),
            HookEvent.SUBAGENT_STOP: lambda: handle_subagent_stop(kwargs.get("stop_hook_active")),
            HookEvent.NOTIFICATION: lambda: handle_notification(kwargs.get("message")),
            HookEvent.PRE_COMPACT: lambda: handle_pre_compact(kwargs.get("trigger"), kwargs.get("custom_instructions")),
            HookEvent.SESSION_START: lambda: handle_session_start(kwargs.get("source")),
            HookEvent.SESSION_END: lambda: handle_session_end(kwargs.get("reason"))
        }
        
        handler = handlers.get(hook_event_name, allow)
        handler()
            
    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"Hook processing error: {e}", err=True)
        raise typer.Exit(1)