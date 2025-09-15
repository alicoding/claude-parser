#!/usr/bin/env python3
"""
Conversation Filtering - 100% Framework Delegation with @LOC_ENFORCEMENT
SRP: Single responsibility for message/hook filtering operations
"""

from typing import Iterator, Dict, Any, List


def filter_messages_by_type(messages: List, message_type: str) -> Iterator:
    """Filter messages by type - 100% built-in filter delegation"""
    return filter(lambda msg: msg.get('type') == message_type, messages)


def filter_messages_by_tool(messages: List, tool_name: str) -> Iterator:
    """Filter messages by tool usage - 100% delegation to existing analyze_tool_usage pattern"""
    return filter(lambda msg: msg.get('tool_use_id') == tool_name or msg.get('tool_name') == tool_name, messages)


def filter_hook_events_by_type(hook_events: List[Dict[str, Any]], hook_type: str, tool: str = None) -> Iterator:
    """Filter hook events - 100% built-in filter delegation"""
    if tool:
        return filter(lambda event: (event.get('hook_event_name') == hook_type and 
                                   event.get('tool_name') == tool), hook_events)
    return filter(lambda event: event.get('hook_event_name') == hook_type, hook_events)


def search_messages_by_content(messages: List, keyword: str) -> Iterator:
    """Search message content - 100% delegation to message utils"""
    from ..messages.utils import get_text
    return filter(lambda msg: keyword.lower() in get_text(msg).lower(), messages)


# Advanced filtering for cross-session context (future enhancement)
def filter_pure_conversation(messages: List) -> Iterator:
    """Filter pure conversation - exclude tool operations and system messages"""
    from ..messages.utils import is_hook_message
    def is_pure_conversation(msg):
        # Must be user or assistant
        if msg.get('type') not in ['user', 'assistant']:
            return False
        # Skip meta messages
        if msg.get('is_meta', False):
            return False
        # Skip compact summaries
        if msg.get('is_compact_summary', False):
            return False
        # Skip hook messages using util
        if is_hook_message(msg):
            return False
        return True
    
    return filter(is_pure_conversation, messages)


def exclude_tool_operations(messages: List) -> Iterator:
    """Exclude tool operation messages - keep only discussion"""
    from ..messages.utils import is_tool_operation, get_text
    def is_not_tool_operation_msg(msg):
        # Use util to check for tool operations
        if is_tool_operation(msg):
            return False

        # Check content for additional patterns
        content = get_text(msg)

        # For assistant messages, check if it's a tool_use
        if msg.get('type') == 'assistant' and '"type": "tool_use"' in content:
            return False

        # Exclude interrupt messages
        if '[Request interrupted' in content:
            return False

        return True

    return filter(is_not_tool_operation_msg, messages)


def exclude_system_summaries(messages: List) -> Iterator:
    """Exclude system summary messages - keep only user/assistant discussion"""
    return filter(lambda msg: msg.type != 'system' and not msg.is_compact_summary, messages)