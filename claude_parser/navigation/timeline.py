#!/usr/bin/env python3
"""
Timeline Operations - 100% Framework Delegation
SRP: UUID-based timeline operations and advanced analytics
"""

from typing import Optional, List, Dict, Any
from more_itertools import first
from itertools import takewhile, dropwhile

def find_message_by_uuid(session, target_uuid: str) -> Optional[Dict[str, Any]]:
    """100% framework delegation: Use session interface to find message"""
    if not session or not session.messages:
        return None
    
    # 100% framework: Delegate to analytics for processing
    from ..analytics import analyze_session
    analytics = analyze_session(session)
    
    # 100% more-itertools: Use first() instead of manual loop
    matching_messages = (
        {
            'uuid': message.uuid,
            'type': getattr(message, 'type', 'unknown'),
            'content': str(getattr(message, 'content', ''))[:200],
            'timestamp': getattr(message, 'timestamp', None)
        }
        for message in session.messages
        if hasattr(message, 'uuid') and message.uuid == target_uuid
    )
    return first(matching_messages, None)

def get_message_sequence(session, start_uuid: str, end_uuid: str) -> List[Dict[str, Any]]:
    """100% framework delegation: Use analytics framework for sequence extraction"""
    if not session or not session.messages:
        return []
    
    # 100% framework: Delegate to analytics for message processing
    from ..analytics import analyze_session
    analytics = analyze_session(session)
    
    # Find messages using framework
    start_msg = find_message_by_uuid(session, start_uuid)
    end_msg = find_message_by_uuid(session, end_uuid)
    
    if not start_msg or not end_msg:
        return []
    
    # 100% itertools: Use dropwhile/takewhile instead of manual stateful loop
    messages_with_uuid = (msg for msg in session.messages if hasattr(msg, 'uuid'))
    
    # Drop messages until we find the start UUID
    from_start = dropwhile(lambda msg: msg.uuid != start_uuid, messages_with_uuid)
    
    # Take messages until we find the end UUID (inclusive)
    sequence_messages = takewhile(lambda msg: msg.uuid != end_uuid, from_start)
    
    # Convert to desired format using framework
    sequence = [
        {'uuid': msg.uuid, 'type': getattr(msg, 'type', 'unknown')}
        for msg in sequence_messages
    ]
    
    return sequence

def get_timeline_summary(session) -> Dict[str, Any]:
    """100% framework delegation: Use analytics framework for summary"""
    if not session or not session.messages:
        return {'total_messages': 0, 'types': {}, 'uuids': []}
    
    # 100% framework delegation to analytics
    from ..analytics import analyze_session
    analytics = analyze_session(session)
    
    # 100% framework delegation: Extract UUIDs using generator
    uuids = [getattr(msg, 'uuid', '') for msg in session.messages if hasattr(msg, 'uuid')]
    return {
        'total_messages': analytics.get('message_count', 0),
        'types': analytics.get('types', {}),
        'uuids': uuids
    }