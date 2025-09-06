"""
Context window service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from typing import Dict, Tuple, Any
from dataclasses import dataclass
from ...core.resources import get_resource_manager
from ...components.context_monitor import ContextMonitor, ContextInfo, ContextStatus
from ...components.context_formatter import ContextFormatter


@dataclass
class ContextWindowInfo:
    """Extended context window information for backward compatibility."""
    total_tokens: int
    context_limit: int
    percentage_used: float
    tokens_remaining: int
    tokens_until_compact: int
    percentage_until_compact: float
    status: ContextStatus
    should_compact: bool
    emoji: str
    message: str

    @property
    def is_critical(self) -> bool:
        """Check if context usage is critical."""
        return self.status in [ContextStatus.RED, ContextStatus.CRITICAL]

    @property
    def needs_attention(self) -> bool:
        """Check if context usage needs attention."""
        return self.status in [ContextStatus.ORANGE, ContextStatus.RED, ContextStatus.CRITICAL]


class ContextWindowService:
    """Clean context window service using ResourceManager pattern."""

    def __init__(self, context_limit: int = None):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        self.context_limit = context_limit or 200_000
        self.monitor = ContextMonitor(self.resources, self.context_limit)
        self.formatter = ContextFormatter(self.resources)

    def analyze(self, total_tokens: int) -> ContextWindowInfo:
        """Analyze context usage using micro-components."""
        info = self.monitor.analyze_usage(total_tokens)

        # Calculate additional fields for backward compatibility
        tokens_remaining = max(0, self.context_limit - total_tokens)
        compact_tokens = int(self.context_limit * 0.9)
        tokens_until_compact = max(0, compact_tokens - total_tokens)
        percentage_until_compact = max(0, (compact_tokens - total_tokens) / self.context_limit)

        emoji = self.formatter._get_emoji(info.status)
        message = f"Context usage: {info.percentage_used*100:.1f}%"

        return ContextWindowInfo(
            total_tokens=info.total_tokens,
            context_limit=info.context_limit,
            percentage_used=info.percentage_used,
            tokens_remaining=tokens_remaining,
            tokens_until_compact=tokens_until_compact,
            percentage_until_compact=percentage_until_compact,
            status=info.status,
            should_compact=info.should_compact,
            emoji=emoji,
            message=message
        )

    def get_simple_status(self, total_tokens: int) -> Tuple[str, float]:
        """Get simple status using micro-component."""
        info = self.monitor.analyze_usage(total_tokens)
        return info.status.value, info.percentage_used

    def should_alert(self, total_tokens: int) -> bool:
        """Check if should alert."""
        info = self.monitor.analyze_usage(total_tokens)
        return info.status in [ContextStatus.ORANGE, ContextStatus.RED, ContextStatus.CRITICAL]

    def format_cli_status(self, total_tokens: int) -> str:
        """Format CLI status using micro-component."""
        info = self.monitor.analyze_usage(total_tokens)
        return self.formatter.format_cli_status(info)

    def get_webhook_payload(self, total_tokens: int) -> Dict[str, Any]:
        """Get webhook payload using micro-component."""
        info = self.monitor.analyze_usage(total_tokens)
        return self.formatter.get_webhook_payload(info)


# Backward Compatibility Class
class ContextWindowManager:
    """Backward compatibility for legacy ContextWindowManager."""

    # Legacy constants
    CONTEXT_LIMIT = 200_000
    COMPACT_THRESHOLD = 0.9
    CRITICAL_THRESHOLD = 0.95
    RED_THRESHOLD = 0.90
    ORANGE_THRESHOLD = 0.75
    YELLOW_THRESHOLD = 0.50

    def __init__(self, context_limit: int = None):
        """Initialize with context window service."""
        self.context_limit = context_limit or self.CONTEXT_LIMIT
        self.compact_point = int(self.context_limit * self.COMPACT_THRESHOLD)
        self.service = ContextWindowService(context_limit)

    def analyze(self, total_tokens: int) -> ContextWindowInfo:
        """Analyze context - redirect to new implementation."""
        return self.service.analyze(total_tokens)

    def get_simple_status(self, total_tokens: int) -> Tuple[str, float]:
        """Get simple status - redirect to new implementation."""
        return self.service.get_simple_status(total_tokens)

    def should_alert(self, total_tokens: int) -> bool:
        """Check should alert - redirect to new implementation."""
        return self.service.should_alert(total_tokens)

    def format_cli_status(self, total_tokens: int) -> str:
        """Format CLI status - redirect to new implementation."""
        return self.service.format_cli_status(total_tokens)

    def get_webhook_payload(self, total_tokens: int) -> Dict[str, Any]:
        """Get webhook payload - redirect to new implementation."""
        return self.service.get_webhook_payload(total_tokens)
