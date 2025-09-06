"""
ContextFormatter micro-component - Format context status for different outputs.

95/5 principle: Simple string formatting, framework handles presentation.
Size: ~12 LOC (LLM-readable in single context)
"""

from typing import Dict, Any
from ..core.resources import ResourceManager
from .context_monitor import ContextInfo, ContextStatus


class ContextFormatter:
    """Micro-component: Format context information for output."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def format_cli_status(self, info: ContextInfo) -> str:
        """Format for CLI output - simple string formatting."""
        emoji = self._get_emoji(info.status)
        percentage = info.percentage_used * 100
        return f"{emoji} Context: {percentage:.1f}% ({info.total_tokens:,}/{info.context_limit:,})"

    def get_webhook_payload(self, info: ContextInfo) -> Dict[str, Any]:
        """Get webhook payload - simple dict construction."""
        return {
            "status": info.status.value,
            "percentage": round(info.percentage_used * 100, 1),
            "tokens": info.total_tokens,
            "limit": info.context_limit,
            "should_compact": info.should_compact,
            "emoji": self._get_emoji(info.status)
        }

    def _get_emoji(self, status: ContextStatus) -> str:
        """Get status emoji - simple mapping."""
        emoji_map = {
            ContextStatus.GREEN: "🟢",
            ContextStatus.YELLOW: "🟡",
            ContextStatus.ORANGE: "🟠",
            ContextStatus.RED: "🔴",
            ContextStatus.CRITICAL: "💀"
        }
        return emoji_map.get(status, "❓")
