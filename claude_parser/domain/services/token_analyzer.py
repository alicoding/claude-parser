"""
Token analyzer service for tracking and analyzing token usage.

SOLID: Single Responsibility - Token analysis only
DDD: Domain service for token analytics
95/5: Uses tokenator library for tracking
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from toolz import filter as toolz_filter
from toolz import pipe

from claude_parser.infrastructure.file_utils import ensure_file_exists
from claude_parser.models.usage import UsageInfo

from ..value_objects.token_service import TokenService, default_token_service


@dataclass
class TokenStats:
    """Token usage statistics."""

    total_input: int = 0
    total_output: int = 0
    total_cache_read: int = 0
    total_cache_created: int = 0
    message_count: int = 0
    cache_hit_rate: float = 0.0
    average_tokens_per_message: float = 0.0
    total_cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Total tokens processed."""
        return (
            self.total_input
            + self.total_output
            + self.total_cache_read
            + self.total_cache_created
        )

    @property
    def cache_savings(self) -> int:
        """Tokens saved through caching."""
        return self.total_cache_read


class TokenAnalyzer:
    """Analyzes token usage patterns in conversations.

    SOLID: Single Responsibility - Token pattern analysis only
    DDD: Uses TokenService value object for calculations
    95/5: Delegates to TokenService, no duplicate pricing logic
    """

    def __init__(self, token_service: Optional[TokenService] = None):
        """Initialize token analyzer.

        Args:
            token_service: Service for token calculations, uses default if None
        """
        self.token_service = token_service or default_token_service
        self.stats_cache = {}

    def analyze_conversation(self, conversation: Any) -> TokenStats:
        """Analyze token usage in a conversation.

        Args:
            conversation: Conversation object with messages

        Returns:
            TokenStats with usage analysis
        """
        stats = TokenStats()

        # Extract assistant messages with usage info
        # Handle both string and enum types
        assistant_messages = pipe(
            conversation.messages,
            lambda msgs: toolz_filter(
                lambda m: str(m.type).lower().endswith("assistant"), msgs
            ),
            lambda msgs: toolz_filter(
                lambda m: hasattr(m, "message")
                and m.message
                and isinstance(m.message, dict),
                msgs,
            ),
            list,
        )

        for msg in assistant_messages:
            if "usage" in msg.message:
                usage_data = msg.message["usage"]
                usage = self._parse_usage(usage_data)

                stats.total_input += usage.input_tokens
                stats.total_output += usage.output_tokens
                stats.total_cache_read += usage.cache_read_input_tokens
                stats.total_cache_created += usage.cache_creation_input_tokens
                stats.message_count += 1

        # Calculate derived stats
        if stats.message_count > 0:
            stats.average_tokens_per_message = stats.total_tokens / stats.message_count

            # Cache hit rate
            total_input = stats.total_input + stats.total_cache_read
            if total_input > 0:
                stats.cache_hit_rate = stats.total_cache_read / total_input

        # Calculate cost using unified service
        stats.total_cost_usd = float(self._calculate_cost_with_service(stats))

        return stats

    def analyze_session_tokens(self, transcript_path: str) -> Dict[str, Any]:
        """Analyze token usage for an entire session.

        Args:
            transcript_path: Path to JSONL transcript

        Returns:
            Detailed token analysis
        """
        from claude_parser import load

        path = ensure_file_exists(transcript_path)
        conversation = load(path)
        stats = self.analyze_conversation(conversation)

        # Find token usage over time
        timeline = self._build_token_timeline(conversation)

        # Identify high token messages
        high_token_messages = self._find_high_token_messages(
            conversation, threshold=5000
        )

        return {
            "stats": stats,
            "timeline": timeline,
            "high_token_messages": high_token_messages,
            "reinject_recommended": stats.total_tokens > 25000,
            "cache_efficiency": {
                "hit_rate": stats.cache_hit_rate,
                "savings": stats.cache_savings,
                "effectiveness": "good" if stats.cache_hit_rate > 0.5 else "poor",
            },
        }

    def _parse_usage(self, usage_data: Dict) -> UsageInfo:
        """Parse usage data into UsageInfo object."""
        return UsageInfo(
            input_tokens=usage_data.get("input_tokens", 0),
            output_tokens=usage_data.get("output_tokens", 0),
            cache_creation_input_tokens=usage_data.get(
                "cache_creation_input_tokens", 0
            ),
            cache_read_input_tokens=usage_data.get("cache_read_input_tokens", 0),
            service_tier=usage_data.get("service_tier"),
        )

    def _calculate_cost(self, stats: TokenStats) -> float:
        """Calculate USD cost using unified token service.

        SOLID: Delegates to TokenService, no duplicate pricing logic
        """
        # Create a synthetic UsageInfo for cost calculation
        usage = UsageInfo(
            input_tokens=stats.total_input,
            output_tokens=stats.total_output,
            cache_creation_input_tokens=stats.total_cache_created,
            cache_read_input_tokens=stats.total_cache_read,
        )
        return float(self.token_service.calculate_usage_cost(usage))

    def _build_token_timeline(self, conversation: Any) -> List[Dict]:
        """Build timeline of token usage."""
        timeline = []
        cumulative = 0

        for msg in conversation.messages:
            if (
                msg.type == "assistant"
                and hasattr(msg, "message")
                and "usage" in msg.message
            ):
                usage = self._parse_usage(msg.message["usage"])
                cumulative += usage.total_tokens

                timeline.append(
                    {
                        "timestamp": msg.timestamp,
                        "tokens": usage.total_tokens,
                        "cumulative": cumulative,
                        "cached": usage.is_cached,
                    }
                )

        return timeline

    def _find_high_token_messages(
        self, conversation: Any, threshold: int = 5000
    ) -> List[Dict]:
        """Find messages that used high token counts."""
        high_token = []

        for i, msg in enumerate(conversation.messages):
            if (
                msg.type == "assistant"
                and hasattr(msg, "message")
                and "usage" in msg.message
            ):
                usage = self._parse_usage(msg.message["usage"])

                if usage.total_tokens > threshold:
                    high_token.append(
                        {
                            "index": i,
                            "timestamp": msg.timestamp,
                            "tokens": usage.total_tokens,
                            "content_preview": msg.text_content[:100]
                            if msg.text_content
                            else "",
                        }
                    )

        return high_token

    def recommend_reinject_points(
        self, conversation: Any, interval: int = 25000
    ) -> List[int]:
        """Recommend message indices for context reinjection.

        Args:
            conversation: Conversation to analyze
            interval: Token interval for reinjection (default 25K)

        Returns:
            List of message indices where reinjection should occur
        """
        reinject_points = []
        cumulative = 0
        last_reinject = 0

        for i, msg in enumerate(conversation.messages):
            if (
                msg.type == "assistant"
                and hasattr(msg, "message")
                and "usage" in msg.message
            ):
                usage = self._parse_usage(msg.message["usage"])
                cumulative += usage.total_tokens

                # Check if we've passed the interval
                if cumulative - last_reinject >= interval:
                    reinject_points.append(i)
                    last_reinject = cumulative

        return reinject_points


# Export main class
__all__ = ["TokenAnalyzer", "TokenStats"]
