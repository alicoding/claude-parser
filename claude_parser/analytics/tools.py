#!/usr/bin/env python3
"""
Tool Usage Analytics
@COMPOSITION: Plain dict processing
"""

from typing import Dict, Any, List
from collections import Counter


def analyze_tool_usage(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze tool usage from session dict"""
    if not session_data:
        return {'tools': {}, 'sequences': [], 'unique_tools': 0}
    
    messages = session_data.get('messages', [])
    if not messages:
        return {'tools': {}, 'sequences': [], 'unique_tools': 0}
    
    # Track tool usage with Counter and sequence
    tool_counter = Counter()
    tool_sequence = []
    
    for msg in messages:
        msg_type = msg.get('type') or msg.get('role', 'unknown')
        
        # Extract tools from assistant messages
        if msg_type == 'assistant' and 'message' in msg:
            content = msg['message'].get('content', [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                        tool_name = item.get('name')
                        if tool_name:
                            tool_counter[tool_name] += 1
                            tool_sequence.append(tool_name)
    
    return {
        'tools': dict(tool_counter),
        'sequences': tool_sequence,
        'unique_tools': len(tool_counter)
    }