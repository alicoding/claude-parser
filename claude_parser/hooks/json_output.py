"""Advanced JSON output for Claude Code hooks.

This module provides the 5% advanced API for users who need
structured JSON responses for specific hook types.

95% of users should use the simple exit_success/exit_block functions.
"""

import sys
from typing import Optional, Dict, Any
import orjson
from toolz import merge, itemfilter


def json_output(
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    hook_type: Optional[str] = None,
    additional_context: Optional[str] = None,
    **kwargs
) -> None:
    """Output JSON response for Claude Code hooks.
    
    Smart JSON output that matches Claude's expectations for each hook type.
    Automatically handles the different formats required by different hooks.
    
    Args:
        decision: The decision ("allow", "deny", "ask" for PreToolUse, etc.)
        reason: Explanation for the decision
        hook_type: The hook event type (auto-detects format)
        additional_context: For UserPromptSubmit and SessionStart
        **kwargs: Additional hook-specific fields
    
    Examples:
        # PreToolUse - uses special format
        json_output(decision="deny", reason="Security", hook_type="PreToolUse")
        
        # UserPromptSubmit - adds context
        json_output(decision="continue", additional_context="Extra info", 
                   hook_type="UserPromptSubmit")
        
        # PostToolUse - simple format
        json_output(decision="continue", reason="OK", hook_type="PostToolUse")
    """
    # PreToolUse uses different structure with hookSpecificOutput
    if hook_type == "PreToolUse":
        # Handle legacy naming (approve -> allow, block -> deny)
        if decision == "approve":
            decision = "allow"
        elif decision == "block":
            decision = "deny"
            
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason
            }
        }
        
    # UserPromptSubmit can add context
    elif hook_type == "UserPromptSubmit":
        output = {
            "decision": decision or "continue",
            "reason": reason
        }
        if additional_context:
            output["hookSpecificOutput"] = {
                "additionalContext": additional_context
            }
            
    # SessionStart can add context - use functional conditional building
    elif hook_type == "SessionStart":
        output = (
            {"hookSpecificOutput": {"additionalContext": additional_context}}
            if additional_context
            else {"decision": "continue"}  # Provide meaningful default instead of empty dict
        )
            
    # Stop/SubagentStop - simple format
    elif hook_type in ("Stop", "SubagentStop"):
        output = {
            "decision": decision or "continue",
            "reason": reason
        }
        
    # PostToolUse and others - simple format
    else:
        output = {
            "decision": decision or "continue",
            "reason": reason
        }
    
    # Add any extra kwargs using functional merge - kwargs override existing
    # Filter kwargs to only include keys not already in output
    filtered_kwargs = itemfilter(lambda item: item[0] not in output, kwargs)
    output = merge(output, filtered_kwargs)
    
    # Output JSON and exit successfully
    print(orjson.dumps(output).decode())
    sys.exit(0)


class AdvancedHooks:
    """Advanced hook-specific convenience methods (5% API).
    
    These are optional convenience methods that generate the correct
    JSON for specific hook types. Most users should use the basic
    exit_success/exit_block functions instead.
    """
    
    @staticmethod
    def allow(reason: str = "Auto-approved") -> None:
        """Allow a PreToolUse request."""
        json_output(decision="allow", reason=reason, hook_type="PreToolUse")
    
    @staticmethod
    def deny(reason: str = "Security violation") -> None:
        """Deny a PreToolUse request."""
        json_output(decision="deny", reason=reason, hook_type="PreToolUse")
    
    @staticmethod
    def ask(reason: str = "User confirmation required") -> None:
        """Ask user for PreToolUse permission."""
        json_output(decision="ask", reason=reason, hook_type="PreToolUse")
    
    @staticmethod
    def add_context(context: str, hook_type: str = "UserPromptSubmit") -> None:
        """Add additional context to UserPromptSubmit or SessionStart."""
        json_output(
            decision="continue",
            additional_context=context,
            hook_type=hook_type
        )
    
    @staticmethod
    def prevent(reason: str = "Must keep processing") -> None:
        """Prevent Stop/SubagentStop from stopping."""
        json_output(decision="prevent", reason=reason, hook_type="Stop")


# Create singleton instance
advanced = AdvancedHooks()