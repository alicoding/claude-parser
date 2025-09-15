#!/usr/bin/env python3
"""
Message utilities - Pure functions operating on dicts
@COMPOSITION: No classes, just functions processing plain dicts
"""

from typing import Dict, Any, Optional, Union


def get_text(msg: Dict[str, Any]) -> str:
    """Extract text content from message dict"""
    content = msg.get('content')
    
    # Handle JSON array format [{"type": "text", "text": "..."}]
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'text':
                return item.get('text', '')
    
    # Handle JSON string that needs parsing
    if isinstance(content, str):
        # Try to parse as JSON first
        if content.startswith('[') and content.endswith(']'):
            try:
                import json
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            return item.get('text', '')
                    # If we parsed JSON but found no text type, return empty
                    return ''
            except json.JSONDecodeError:
                pass
        # Return as-is if not JSON or parsing failed
        return content
    
    # Fallback to message field
    if msg.get('message') and isinstance(msg['message'], dict):
        msg_content = msg['message'].get('content')
        if isinstance(msg_content, str):
            return msg_content
    
    return ''


def get_token_usage(msg: Dict[str, Any]) -> Dict[str, int]:
    """Extract token usage from message dict"""
    # Direct usage field
    if 'usage' in msg and isinstance(msg['usage'], dict):
        return msg['usage']
    
    # Nested in message field
    if msg.get('message') and isinstance(msg['message'], dict):
        if 'usage' in msg['message']:
            return msg['message']['usage']
    
    return {}


def get_model(msg: Dict[str, Any]) -> Optional[str]:
    """Extract model name from message dict"""
    if msg.get('message') and isinstance(msg['message'], dict):
        return msg['message'].get('model')
    return msg.get('model')


def is_hook_message(msg: Dict[str, Any]) -> bool:
    """Check if message is a hook event"""
    text = get_text(msg)
    return '-hook>' in text


def is_tool_operation(msg: Dict[str, Any]) -> bool:
    """Check if message is a tool operation"""
    return bool(msg.get('tool_use_id') or msg.get('tool_result'))