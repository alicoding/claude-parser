#!/usr/bin/env python3
"""
Checkpoint Detection - 100% Framework Delegation with @LOC_ENFORCEMENT
SRP: Single responsibility for checkpoint detection operations
@COMPOSITION: Works with plain dicts
"""

from typing import Optional, Dict, Any
from more_itertools import first


def find_current_checkpoint(session_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find last file operation - delegates to DuckDB for JSON parsing"""
    if not session_data:
        return None

    # Get JSONL path from metadata for SQL query
    jsonl_path = session_data.get('metadata', {}).get('transcript_path')
    if not jsonl_path:
        # Fallback to simple iteration if no path
        messages = session_data.get('messages', [])
        for msg in reversed(messages):
            if msg.get('toolUseResult') and 'filePath' in str(msg.get('toolUseResult', '')):
                return {
                    'uuid': msg.get('uuid', 'unknown'),
                    'timestamp': msg.get('timestamp'),
                    'content_preview': 'File operation found',
                    'triggered_tool': 'unknown'
                }
        return None

    # Use DuckDB to find last file operation - simple string matching
    import duckdb
    result = duckdb.sql(f"""
        SELECT
            uuid,
            timestamp,
            toolUseResult
        FROM '{jsonl_path}'
        WHERE toolUseResult IS NOT NULL
          AND toolUseResult LIKE '%"filePath"%'
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()

    if result:
        import json
        # Parse the toolUseResult to get file path
        try:
            tool_data = json.loads(result[2]) if isinstance(result[2], str) else {}
            file_path = tool_data.get('filePath', 'unknown')
            tool_type = tool_data.get('type', 'unknown')
        except:
            file_path = 'unknown'
            tool_type = 'unknown'

        return {
            'uuid': str(result[0]),
            'timestamp': result[1],
            'file_path': file_path,
            'content_preview': 'File operation found',
            'triggered_tool': tool_type
        }

    return None


def _find_triggering_user_message(raw_data: list, file_op_uuid: str, tool_name: str) -> Optional[Dict[str, Any]]:
    """Find the user message that triggered the file operation"""
    # Find the file operation event
    file_event = None
    for event in raw_data:
        if event.get('uuid') == file_op_uuid:
            file_event = event
            break
    
    if not file_event:
        return None
    
    file_timestamp = file_event.get('timestamp', '')
    
    # Walk backwards to find user message before this timestamp
    for event in reversed(raw_data):
        msg_data = event.get('message', {})
        msg_role = msg_data.get('role') or event.get('type')
        
        if (msg_role == 'user' and 
            event.get('timestamp', '') < file_timestamp):
            return {
                'user_uuid': event.get('uuid'),
                'timestamp': event.get('timestamp'),
                'content_preview': f"User message at {event.get('timestamp')}",
                'triggered_tool': tool_name
            }
    
    return None