"""
StatsCalculator micro-component - Basic conversation statistics.

95/5 principle: Simple calculations, let Python handle the math.
Size: ~20 LOC (LLM-readable in single context)
"""

from typing import List, Dict, Any
from ..core.resources import ResourceManager
from ..models import Message


class StatsCalculator:
    """Micro-component: Calculate conversation statistics."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources
        self.token_counter = resources.get_token_encoder()

    def calculate_basic_stats(self, messages: List[Message]) -> Dict[str, Any]:
        """Calculate basic statistics - simple Python logic."""
        total = len(messages)
        user_count = sum(1 for m in messages if 'user' in m.__class__.__name__.lower())
        assistant_count = sum(1 for m in messages if 'assistant' in m.__class__.__name__.lower())

        return {
            'total_messages': total,
            'user_messages': user_count,
            'assistant_messages': assistant_count,
        }
