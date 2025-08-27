"""
Message navigation delegate.

SOLID: Single Responsibility - Only navigation/positional operations.
95/5: Using functional approaches where possible.
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import Message, Summary


class MessageNavigator:
    """
    Handles navigation and positional operations on messages.
    Extracted from Conversation to follow SRP.
    """
    
    def __init__(self, messages: List["Message"]):
        """Initialize with messages to navigate."""
        self._messages = messages
    
    def get_by_uuid(self, uuid: str) -> Optional["Message"]:
        """Get message by UUID."""
        for msg in self._messages:
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                return msg
        return None
    
    def get_surrounding(
        self, uuid: str, before: int = 2, after: int = 2
    ) -> List["Message"]:
        """Get messages surrounding a specific UUID."""
        for i, msg in enumerate(self._messages):
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                start_idx = max(0, i - before)
                end_idx = min(len(self._messages), i + after + 1)
                return self._messages[start_idx:end_idx]
        return []
    
    def get_thread_from(self, uuid: str) -> List["Message"]:
        """Get thread of messages starting from UUID."""
        start_idx = None
        for i, msg in enumerate(self._messages):
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                start_idx = i
                break
        
        if start_idx is None:
            return []
        
        return self._messages[start_idx:]
    
    def between_timestamps(
        self, start_timestamp: str, end_timestamp: str
    ) -> List["Message"]:
        """Get messages between two timestamps."""
        result = []
        for msg in self._messages:
            if hasattr(msg, "timestamp") and msg.timestamp:
                if start_timestamp <= msg.timestamp <= end_timestamp:
                    result.append(msg)
        return result
    
    def before_summary(self, limit: int = 10) -> List["Message"]:
        """Get messages before the last summary."""
        from ...models import Summary
        
        # Find last summary index
        summary_indices = [
            i for i, msg in enumerate(self._messages) if isinstance(msg, Summary)
        ]
        
        if not summary_indices:
            # No summary, return last 'limit' messages
            return (
                self._messages[-limit:]
                if limit < len(self._messages)
                else self._messages[:]
            )
        
        # Get messages before last summary
        last_summary_idx = summary_indices[-1]
        start_idx = max(0, last_summary_idx - limit)
        return self._messages[start_idx:last_summary_idx]
    
    def get_at_index(self, index: int) -> Optional["Message"]:
        """Get message at specific index."""
        if 0 <= index < len(self._messages):
            return self._messages[index]
        return None
    
    def get_slice(self, start: int, end: int) -> List["Message"]:
        """Get slice of messages."""
        return self._messages[start:end]