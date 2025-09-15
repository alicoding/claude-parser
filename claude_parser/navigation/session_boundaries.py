#!/usr/bin/env python3
"""
Session Boundary Detection - Using discovered JSONL fields
SRP: Find session start/end boundaries in JSONL
"""

from typing import Optional, Tuple
from more_itertools import first


def find_current_session_boundaries(session) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the boundaries of the current session.
    
    Returns:
        (start_uuid, end_uuid) where:
        - start_uuid: UUID after last compact summary (or first message)
        - end_uuid: None (means current position)
    """
    if not session or not session.messages:
        return None, None
    
    # Find the most recent compact summary
    # Note: is_compact_summary can be None (Polars fills missing fields with None)
    compact_summaries = [
        (i, msg) for i, msg in enumerate(session.messages)
        if getattr(msg, 'is_compact_summary', False) is True
    ]
    
    if compact_summaries:
        # Get the last compact summary
        last_compact_idx, last_compact = compact_summaries[-1]
        
        # Session starts AFTER the compact summary
        if last_compact_idx + 1 < len(session.messages):
            start_msg = session.messages[last_compact_idx + 1]
            return start_msg.uuid, None
        else:
            # Compact was the last message (edge case)
            return last_compact.uuid, None
    else:
        # No compact summaries - session starts at beginning
        return session.messages[0].uuid, None


def get_session_token_range(session, start_uuid: str, end_uuid: Optional[str] = None):
    """
    Get all messages between start and end UUIDs for token counting.
    
    Args:
        session: The RichSession object
        start_uuid: Starting boundary UUID
        end_uuid: Ending boundary UUID (None means to end of session)
    
    Returns:
        List of messages in the range
    """
    if not session or not session.messages or not start_uuid:
        return []
    
    # Find start position
    start_idx = None
    for i, msg in enumerate(session.messages):
        if msg.uuid == start_uuid:
            start_idx = i
            break
    
    if start_idx is None:
        return []
    
    # If no end_uuid, return from start to end
    if end_uuid is None:
        return session.messages[start_idx:]
    
    # Find end position and return range
    for i, msg in enumerate(session.messages[start_idx:], start=start_idx):
        if msg.uuid == end_uuid:
            return session.messages[start_idx:i+1]
    
    # End UUID not found, return to end
    return session.messages[start_idx:]