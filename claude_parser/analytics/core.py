#!/usr/bin/env python3
"""
Analytics Core - @COMPOSITION Pattern with Plain Dicts
SRP: Basic session analytics
@SINGLE_SOURCE_TRUTH: Process plain dicts only
"""

from typing import Dict, Any
from collections import Counter


def analyze_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze session from plain dict"""
    if not session_data:
        return {'message_count': 0, 'types': {}, 'tools': {}}
    
    messages = session_data.get('messages', [])
    if not messages:
        return {'message_count': 0, 'types': {}, 'tools': {}}
    
    # Use Counter for efficient aggregation
    type_counter = Counter()
    tool_counter = Counter()
    
    for msg in messages:
        msg_type = msg.get('type') or msg.get('role', 'unknown')
        type_counter[msg_type] += 1
        
        # Check for tool usage in message content
        if msg_type == 'assistant' and 'message' in msg:
            content = msg['message'].get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool_name = item.get('name')
                        if tool_name:
                            tool_counter[tool_name] += 1
    
    return {
        'message_count': len(messages),
        'types': dict(type_counter),
        'tools': dict(tool_counter),
        'total_tools': sum(tool_counter.values())
    }