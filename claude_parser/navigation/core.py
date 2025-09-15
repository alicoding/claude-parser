#!/usr/bin/env python3
"""
Navigation Core - 100% Framework Delegation
SRP: Basic message navigation operations only
"""

from more_itertools import first, last, nth


def get_latest_message(messages):
    """Get the most recent message - 100% more-itertools"""
    return last(messages, None)


def get_latest_user_message(messages):
    """Get the most recent real user message (not tool results) - 100% framework"""
    # 100% delegation to filtering domain
    from ..filtering import filter_pure_conversation, exclude_tool_operations
    
    # Get pure conversation (excludes meta, summaries)
    pure_messages = filter_pure_conversation(messages)
    
    # Filter to user messages only
    user_messages = filter(lambda msg: msg.get('type') == 'user', pure_messages)
    
    # Exclude tool operations (tool results)
    real_user_messages = exclude_tool_operations(user_messages)
    
    # Return the last one using more-itertools
    return last(real_user_messages, None)


def get_latest_assistant_message(messages):
    """Get the most recent assistant message - 100% framework"""
    # 100% delegation to filtering domain
    from ..filtering import filter_pure_conversation, exclude_tool_operations
    
    # Get pure conversation (excludes meta, summaries, hooks)
    pure_messages = filter_pure_conversation(messages)
    
    # Filter to assistant messages only
    assistant_messages = filter(lambda msg: msg.get('type') == 'assistant', pure_messages)
    
    # Exclude tool operations (tool_use messages)
    real_assistant_messages = exclude_tool_operations(assistant_messages)
    
    # Return the last one using more-itertools
    return last(real_assistant_messages, None)


def get_first_message(messages):
    """Get the first message - 100% more-itertools"""
    return first(messages, None)


def get_previous_message(messages):
    """Get the second-to-last message - 100% more-itertools"""
    return nth(reversed(messages), 1, None)


def jump_to_message(messages, position: int):
    """Jump to message at human position (1-based) - 100% more-itertools"""
    return nth(messages, position - 1, None)