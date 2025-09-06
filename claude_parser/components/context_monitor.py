"""
ContextMonitor micro-component - Monitor context window usage.

95/5 principle: Simple percentage calculations, framework handles data structures.
Size: ~15 LOC (LLM-readable in single context)
"""

from typing import Tuple
from dataclasses import dataclass
from enum import Enum
from ..core.resources import ResourceManager


class ContextStatus(Enum):
    """Context window status levels."""
    GREEN = "green"      # < 50% used
    YELLOW = "yellow"    # 50-75% used
    ORANGE = "orange"    # 75-90% used
    RED = "red"          # > 90% used (auto-compact imminent)
    CRITICAL = "critical" # > 95% used (very close to limit)


@dataclass
class ContextInfo:
    """Context window information."""
    total_tokens: int
    context_limit: int
    percentage_used: float
    status: ContextStatus
    should_compact: bool


class ContextMonitor:
    """Micro-component: Monitor context window usage."""

    def __init__(self, resources: ResourceManager, context_limit: int = 200_000):
        """Initialize with injected resources."""
        self.resources = resources
        self.context_limit = context_limit
        self.compact_threshold = 0.9

    def analyze_usage(self, total_tokens: int) -> ContextInfo:
        """Analyze context usage - simple percentage calculation."""
        percentage = total_tokens / self.context_limit
        status = self._get_status(percentage)
        should_compact = percentage >= self.compact_threshold

        return ContextInfo(
            total_tokens=total_tokens,
            context_limit=self.context_limit,
            percentage_used=percentage,
            status=status,
            should_compact=should_compact
        )

    def _get_status(self, percentage: float) -> ContextStatus:
        """Get status from percentage - simple threshold logic."""
        if percentage >= 0.95:
            return ContextStatus.CRITICAL
        elif percentage >= 0.90:
            return ContextStatus.RED
        elif percentage >= 0.75:
            return ContextStatus.ORANGE
        elif percentage >= 0.50:
            return ContextStatus.YELLOW
        else:
            return ContextStatus.GREEN
