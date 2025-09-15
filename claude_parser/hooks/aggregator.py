#!/usr/bin/env python3
"""
Hook Result Aggregator - ANY block = whole fail policy
@SINGLE_SOURCE_TRUTH: One place for aggregation logic
@NO_MANUAL_LOOPS: List comprehensions only
@LOC_ENFORCEMENT: <80 LOC
"""

import json
from typing import List, Tuple, Optional, Any


def aggregate_results(event_type: str, results: List[Tuple[str, Optional[str]]]) -> Tuple[Any, int]:
    """Aggregate plugin results based on hook event type
    
    Policy: ANY block = whole operation fails
    Returns: (output, exit_code)
    """
    # @NO_MANUAL_LOOPS: Use list comprehensions
    blocks = [msg for action, msg in results if action == "block" and msg]
    allows = [msg for action, msg in results if action == "allow" and msg]
    
    # ANY block = fail
    if blocks:
        return _format_block(event_type, blocks), 2
    
    # All allow = success with optional context
    if allows:
        return _format_allow(event_type, allows), 0

    # PostToolUse always needs JSON output
    if event_type == "PostToolUse":
        return _format_allow(event_type, []), 0

    # No output needed for other events
    return None, 0


def _format_block(event_type: str, reasons: List[str]) -> Any:
    """Format block response based on event type"""
    combined_reason = "; ".join(reasons)
    
    if event_type == "PreToolUse":
        # PreToolUse uses specific format
        return json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": combined_reason
            }
        })
    
    # Other events use generic block format
    return json.dumps({
        "decision": "block",
        "reason": combined_reason
    })


def _format_allow(event_type: str, contexts: List[str]) -> Any:
    """Format allow response with contexts based on event type"""
    combined_context = "\n".join(contexts)
    
    if event_type in ["PostToolUse", "UserPromptSubmit", "SessionStart"]:
        # These events support additionalContext
        return json.dumps({
            "hookSpecificOutput": {
                "hookEventName": event_type,
                "additionalContext": combined_context
            }
        })
    
    # PreToolUse with context (informational)
    if event_type == "PreToolUse":
        return json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": combined_context
            }
        })
    
    # Other events don't output for allow
    return None