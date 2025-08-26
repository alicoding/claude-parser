"""
Context Window Manager - Monitor and alert on context usage.

CRITICAL for workflow automation - detects when approaching auto-compact threshold.
Enables programmatic monitoring without watching Claude Code UI.

SOLID: Single Responsibility - Context window monitoring only
95/5: Simple percentage API for common use, detailed info available
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class ContextStatus(Enum):
    """Context window status levels."""

    GREEN = "green"  # < 50% used
    YELLOW = "yellow"  # 50-75% used
    ORANGE = "orange"  # 75-90% used
    RED = "red"  # > 90% used (auto-compact imminent)
    CRITICAL = "critical"  # > 95% used (very close to limit)


@dataclass
class ContextWindowInfo:
    """Detailed context window information."""

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
        return self.status in [
            ContextStatus.ORANGE,
            ContextStatus.RED,
            ContextStatus.CRITICAL,
        ]


class ContextWindowManager:
    """
    Manages context window monitoring and auto-compact detection.

    Essential for automated workflows - provides programmatic access
    to context usage without needing to watch Claude Code UI.
    """

    # Claude 3.5 Sonnet context limits
    CONTEXT_LIMIT = 200_000  # 200K tokens
    COMPACT_THRESHOLD = 0.9  # Auto-compact at 90% (180K tokens)

    # Alert thresholds
    CRITICAL_THRESHOLD = 0.95  # 95% - very close to limit
    RED_THRESHOLD = 0.90  # 90% - auto-compact imminent
    ORANGE_THRESHOLD = 0.75  # 75% - getting high
    YELLOW_THRESHOLD = 0.50  # 50% - halfway there

    def __init__(self, context_limit: int = None):
        """Initialize with optional custom context limit."""
        self.context_limit = context_limit or self.CONTEXT_LIMIT
        self.compact_point = int(self.context_limit * self.COMPACT_THRESHOLD)

    def analyze(self, total_tokens: int) -> ContextWindowInfo:
        """
        Analyze context window usage and provide detailed info.

        This is the main API for monitoring context usage programmatically.

        Args:
            total_tokens: Current total token count

        Returns:
            ContextWindowInfo with all details needed for automation
        """
        # Calculate percentages
        percentage_used = (total_tokens / self.context_limit) * 100
        tokens_remaining = max(0, self.context_limit - total_tokens)
        tokens_until_compact = max(0, self.compact_point - total_tokens)
        percentage_until_compact = (tokens_until_compact / self.context_limit) * 100

        # Determine status
        status = self._get_status(percentage_used / 100)

        # Should compact?
        should_compact = total_tokens >= self.compact_point

        # Get emoji and message
        emoji = self._get_emoji(status)
        message = self._format_message(
            percentage_used, tokens_until_compact, should_compact
        )

        return ContextWindowInfo(
            total_tokens=total_tokens,
            context_limit=self.context_limit,
            percentage_used=percentage_used,
            tokens_remaining=tokens_remaining,
            tokens_until_compact=tokens_until_compact,
            percentage_until_compact=percentage_until_compact,
            status=status,
            should_compact=should_compact,
            emoji=emoji,
            message=message,
        )

    def get_simple_status(self, total_tokens: int) -> Tuple[str, float]:
        """
        95% use case - Simple status check.

        Args:
            total_tokens: Current total token count

        Returns:
            Tuple of (status_emoji, percentage_until_compact)

        Example:
            emoji, percent = manager.get_simple_status(150000)
            # Returns: ("🟡", 20.0)  # Yellow status, 20% until compact
        """
        info = self.analyze(total_tokens)
        return info.emoji, info.percentage_until_compact

    def should_alert(self, total_tokens: int) -> bool:
        """
        Check if usage level warrants an alert.

        Useful for automation - trigger notifications when true.

        Args:
            total_tokens: Current total token count

        Returns:
            True if usage >= 75% (orange/red/critical)
        """
        info = self.analyze(total_tokens)
        return info.needs_attention

    def format_cli_status(self, total_tokens: int) -> str:
        """
        Format status for CLI display.

        Args:
            total_tokens: Current total token count

        Returns:
            Formatted string for terminal display
        """
        info = self.analyze(total_tokens)

        # Build status bar
        bar_length = 20
        filled = int(bar_length * (info.percentage_used / 100))
        bar = "█" * filled + "░" * (bar_length - filled)

        return (
            f"{info.emoji} Context: [{bar}] {info.percentage_used:.1f}%\n"
            f"   {total_tokens:,}/{self.context_limit:,} tokens\n"
            f"   {info.message}"
        )

    def _get_status(self, percentage: float) -> ContextStatus:
        """Determine status based on percentage."""
        if percentage >= self.CRITICAL_THRESHOLD:
            return ContextStatus.CRITICAL
        elif percentage >= self.RED_THRESHOLD:
            return ContextStatus.RED
        elif percentage >= self.ORANGE_THRESHOLD:
            return ContextStatus.ORANGE
        elif percentage >= self.YELLOW_THRESHOLD:
            return ContextStatus.YELLOW
        else:
            return ContextStatus.GREEN

    def _get_emoji(self, status: ContextStatus) -> str:
        """Get emoji for status level."""
        return {
            ContextStatus.GREEN: "🟢",
            ContextStatus.YELLOW: "🟡",
            ContextStatus.ORANGE: "🟠",
            ContextStatus.RED: "🔴",
            ContextStatus.CRITICAL: "🚨",
        }.get(status, "⚪")

    def _format_message(
        self, percentage: float, tokens_until_compact: int, should_compact: bool
    ) -> str:
        """Format human-readable status message."""
        if should_compact:
            return "⚠️ AUTO-COMPACT TRIGGERED! Context will be summarized."
        elif percentage >= 95:
            return (
                f"🚨 CRITICAL: Only {tokens_until_compact:,} tokens until auto-compact!"
            )
        elif percentage >= 90:
            return f"🔴 WARNING: {tokens_until_compact:,} tokens until auto-compact"
        elif percentage >= 75:
            return f"🟠 CAUTION: {percentage:.0f}% used, approaching limit"
        elif percentage >= 50:
            return f"🟡 NOTICE: {percentage:.0f}% of context used"
        else:
            return f"🟢 OK: {tokens_until_compact:,} tokens until auto-compact"

    def get_webhook_payload(self, total_tokens: int) -> Dict:
        """
        Get webhook-ready payload for external notifications.

        Useful for integrating with Slack, Discord, etc.

        Args:
            total_tokens: Current total token count

        Returns:
            Dict with webhook-friendly data
        """
        info = self.analyze(total_tokens)

        return {
            "text": f"{info.emoji} Claude Context: {info.percentage_used:.1f}% used",
            "status": info.status.value,
            "critical": info.is_critical,
            "percentage_used": info.percentage_used,
            "percentage_until_compact": info.percentage_until_compact,
            "tokens_used": total_tokens,
            "tokens_limit": self.context_limit,
            "tokens_until_compact": info.tokens_until_compact,
            "should_compact": info.should_compact,
            "message": info.message,
        }


# Export main class
__all__ = ["ContextWindowManager", "ContextWindowInfo", "ContextStatus"]
