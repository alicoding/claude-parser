"""Advanced JSON output for Claude Code hooks.

This module provides the 5% advanced API for users who need
structured JSON responses for specific hook types.

95% of users should use the simple exit_success/exit_block functions.
"""

import sys
from typing import Optional

import orjson
from toolz import itemfilter, merge


def json_output(
    decision: Optional[str] = None,
    reason: Optional[str] = None,
    hook_type: Optional[str] = None,
    additional_context: Optional[str] = None,
    continue_processing: Optional[bool] = None,
    stop_reason: Optional[str] = None,
    suppress_output: bool = False,
    system_message: Optional[str] = None,
    **kwargs,
) -> None:
    """Output JSON response for Claude Code hooks.

    Smart JSON output that matches Claude's expectations for each hook type.
    Automatically handles the different formats required by different hooks.

    Args:
        decision: The decision ("allow", "deny", "ask" for PreToolUse, etc.)
        reason: Explanation for the decision
        hook_type: The hook event type (auto-detects format)
        additional_context: For UserPromptSubmit and SessionStart
        continue_processing: Whether Claude should continue (default: True)
        stop_reason: Message shown when continue is False
        suppress_output: Hide stdout from transcript mode
        system_message: Optional warning message shown to user
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
                "permissionDecisionReason": reason,
            }
        }

    # UserPromptSubmit can add context
    elif hook_type == "UserPromptSubmit":
        output = {"decision": decision or "continue", "reason": reason}
        if additional_context:
            output["hookSpecificOutput"] = {"additionalContext": additional_context}

    # SessionStart can add context - use functional conditional building
    elif hook_type == "SessionStart":
        output = (
            {"hookSpecificOutput": {"additionalContext": additional_context}}
            if additional_context
            else {
                "decision": "continue"
            }  # Provide meaningful default instead of empty dict
        )

    # Stop/SubagentStop - simple format
    elif hook_type in ("Stop", "SubagentStop"):
        output = {"decision": decision or "continue", "reason": reason}

    # PostToolUse and others - simple format
    else:
        output = {"decision": decision or "continue", "reason": reason}

    # Add common fields available to all hook types
    common_fields = {}
    if continue_processing is not None:
        common_fields["continue"] = continue_processing
    if stop_reason:
        common_fields["stopReason"] = stop_reason
    if suppress_output:
        common_fields["suppressOutput"] = suppress_output
    if system_message:
        common_fields["systemMessage"] = system_message

    # Add any extra kwargs using functional merge - kwargs override existing
    # Filter kwargs to only include keys not already in output
    filtered_kwargs = itemfilter(lambda item: item[0] not in output, kwargs)
    output = merge(output, common_fields, filtered_kwargs)

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
            decision="continue", additional_context=context, hook_type=hook_type
        )

    @staticmethod
    def prevent(reason: str = "Must keep processing") -> None:
        """Prevent Stop/SubagentStop from stopping."""
        json_output(decision="prevent", reason=reason, hook_type="Stop")

    @staticmethod
    def accept(reason: str = "Tool results accepted") -> None:
        """Accept PostToolUse results."""
        json_output(decision="continue", reason=reason, hook_type="PostToolUse")

    @staticmethod
    def challenge(reason: str = "Tool results challenged") -> None:
        """Challenge PostToolUse results (blocks with feedback to Claude)."""
        json_output(decision="block", reason=reason, hook_type="PostToolUse")

    @staticmethod
    def ignore() -> None:
        """Ignore PostToolUse results (no feedback to Claude)."""
        json_output(decision="continue", hook_type="PostToolUse")

    @staticmethod
    def block_prompt(reason: str = "Prompt blocked by policy") -> None:
        """Block UserPromptSubmit from processing."""
        json_output(decision="block", reason=reason, hook_type="UserPromptSubmit")

    @staticmethod
    def halt(reason: str = "Processing halted") -> None:
        """Immediately halt all processing (universal method)."""
        json_output(continue_processing=False, stop_reason=reason)


# Create singleton instance
advanced = AdvancedHooks()


# Convenience functions for common actions
def halt(reason: str = "Processing halted") -> None:
    """Universal halt function - stops processing immediately."""
    json_output(continue_processing=False, stop_reason=reason)
