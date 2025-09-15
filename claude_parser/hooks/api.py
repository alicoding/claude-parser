#!/usr/bin/env python3
"""
Claude Parser Hooks API - Semantic Public Interface
@UTIL_FIRST: All functions delegate to 2 utils internally
@SEMANTIC_INTERFACE: Public API uses business language
"""

from .utils import read_stdin, write_output
from typing import Dict, Any, Optional, Callable


# Core I/O (delegates to utils)
def parse_hook_input() -> Dict[str, Any]:
    """Parse hook input from stdin"""
    return read_stdin()


# Semantic API for better UX (all use same 2 utils)
def allow_operation(reason: str = ""):
    """Allow the operation (PreToolUse)"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "permissionDecisionReason": reason
        }
    }
    write_output(output, 0)


def block_operation(reason: str):
    """Block the operation (PreToolUse/PostToolUse/Stop)"""
    write_output({"decision": "block", "reason": reason}, 0)


def request_approval(reason: str):
    """Request user approval (PreToolUse)"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason
        }
    }
    write_output(output, 0)


def add_context(text: str):
    """Add context for Claude (UserPromptSubmit/SessionStart)"""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text
        }
    }
    write_output(output, 0)


def execute_hook(plugin_callback: Callable) -> None:
    """Execute hook with plugin callback
    
    @SIMPLIFIED: Just read, callback, output
    """
    # Read
    context = read_stdin()
    
    # Callback
    try:
        # Load session if needed
        from ..main import load_session
        session = None
        if context.get('transcript_path'):
            session = load_session(context['transcript_path'])
        
        # Execute callback
        hook_name = context.get('hook_event_name', 'unknown')
        result = plugin_callback(hook_name, context, session)
        
        # Output whatever callback returns
        if result:
            write_output(result, 0)
        else:
            write_output(None, 0)  # Success, no output
            
    except Exception as e:
        write_output(f"Plugin error: {e}", 1)


# Public exports - semantic for users
__all__ = [
    'parse_hook_input',
    'allow_operation',
    'block_operation',
    'request_approval',
    'add_context',
    'execute_hook',
]