"""
TokenUsageAnalyzer micro-component - Analyze token usage patterns.

95/5 principle: Simple token calculations, framework handles data structures.
Size: ~20 LOC (LLM-readable in single context)
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from ..core.resources import ResourceManager
from ..models import Message


@dataclass
class TokenStats:
    """Simple token statistics."""
    total_input: int = 0
    total_output: int = 0
    total_cache_read: int = 0
    total_cache_created: int = 0
    message_count: int = 0

    @property
    def total_tokens(self) -> int:
        return self.total_input + self.total_output + self.total_cache_read + self.total_cache_created

    @property
    def cache_hit_rate(self) -> float:
        total_input = self.total_input + self.total_cache_read
        return self.total_cache_read / total_input if total_input > 0 else 0.0


class TokenUsageAnalyzer:
    """Micro-component: Analyze token usage patterns."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def analyze_usage(self, messages: List[Message]) -> TokenStats:
        """Analyze token usage - simple calculation logic."""
        stats = TokenStats()

        # Find assistant messages with usage data
        for msg in messages:
            if hasattr(msg, 'message') and msg.message and isinstance(msg.message, dict):
                if 'usage' in msg.message:
                    usage = msg.message['usage']
                    stats.total_input += usage.get('input_tokens', 0)
                    stats.total_output += usage.get('output_tokens', 0)
                    stats.total_cache_read += usage.get('cache_read_input_tokens', 0)
                    stats.total_cache_created += usage.get('cache_creation_input_tokens', 0)
                    stats.message_count += 1

        return stats
