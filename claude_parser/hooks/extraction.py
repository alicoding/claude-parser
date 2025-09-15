#!/usr/bin/env python3
"""
Hook Event Extraction - Pure dict processing with utility functions
Domain: Hooks - responsible for extracting hook events from sessions
"""

from typing import List, Dict, Any
from ..messages.utils import get_text


def extract_hook_events(session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract hook events from session data dict - @DATA_DRIVEN approach"""
    hook_events = []
    
    # @DATA_DRIVEN: Get metadata from wherever it exists
    metadata = session_data.get('metadata', {})
    transcript_path = metadata.get('transcript_path')
    if not transcript_path:
        # Try to find it in raw_data or other locations
        return hook_events
    
    # Get messages from session
    messages = session_data.get('messages', [])
    if not messages:
        return hook_events
    
    # @DATA_DRIVEN: Find session context from ANY message that has it
    cwd = None
    session_id = session_data.get('session_id')
    
    for msg in messages:
        if not cwd and 'cwd' in msg:
            cwd = msg['cwd']
        if not session_id and 'session_id' in msg:
            session_id = msg['session_id']
        if cwd and session_id:
            break
    
    if not transcript_path:  # Minimum requirement
        return hook_events
    
    # Process messages by type
    for msg in messages:
        msg_type = msg.get('type') or msg.get('role')
        
        # Extract PreToolUse events from assistant messages
        if msg_type == 'assistant':
            message_data = msg.get('message', {})
            content = message_data.get('content', [])
            if isinstance(content, list):
                for item in content:
                    if (isinstance(item, dict) and 
                        item.get('type') == 'tool_use' and 
                        item.get('name')):
                        hook_events.append({
                            'hook_event_name': 'PreToolUse',
                            'session_id': session_id,
                            'transcript_path': transcript_path,
                            'cwd': cwd,
                            'tool_name': item.get('name'),
                            'tool_input': str(item.get('input', ''))
                        })
        
        # Extract UserPromptSubmit events from user messages
        elif msg_type == 'user':
            prompt_text = get_text(msg)
            if prompt_text and prompt_text.strip():
                hook_events.append({
                    'hook_event_name': 'UserPromptSubmit',
                    'session_id': session_id,
                    'transcript_path': transcript_path,
                    'cwd': cwd,
                    'prompt': prompt_text
                })
    
    return hook_events