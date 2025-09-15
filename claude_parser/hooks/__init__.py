#!/usr/bin/env python3
"""
Claude Parser Hooks SDK - @UTIL_FIRST Implementation
Semantic public API with internal util delegation
"""

from .app import app
from .models import HookEvent
from .handlers import handle_pre_tool_use, handle_post_tool_use, handle_user_prompt
from .api import (
    parse_hook_input,
    allow_operation,
    block_operation, 
    request_approval,
    add_context,
    execute_hook
)
from .extraction import extract_hook_events
from .request import HookRequest

__all__ = [
    # CLI Interface
    "app",
    # Semantic API (@SEMANTIC_INTERFACE)
    "parse_hook_input",
    "allow_operation",
    "block_operation",
    "request_approval", 
    "add_context",
    "execute_hook",
    # Hook Event Extraction
    "extract_hook_events",
    # Shared Components
    "HookEvent",
    "handle_pre_tool_use",
    "handle_post_tool_use", 
    "handle_user_prompt",
    # New HookRequest API
    "HookRequest"
]