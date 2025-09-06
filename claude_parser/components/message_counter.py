"""
MessageCounter micro-component - Message statistics.

95/5 principle: Simple counting logic, framework handles data structures.
Size: ~15 LOC (LLM-readable in single context)
"""

from typing import List, Dict
from ..core.resources import ResourceManager
from ..models import Message


class MessageCounter:
    """Micro-component: Count messages by type."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def count_by_type(self, messages: List[Message]) -> Dict[str, int]:
        """Count messages by type - simple Python logic."""
        counts = {}
        for msg in messages:
            msg_type = msg.__class__.__name__
            counts[msg_type] = counts.get(msg_type, 0) + 1
        return counts
