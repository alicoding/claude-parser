"""Analytics analyzer for conversations.

SOLID: Single Responsibility orchestrator that delegates to focused analyzers.
DDD: Composes domain services for comprehensive analysis.
95/5: Uses specialized classes, minimal orchestration logic.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..domain.entities.conversation import Conversation
from ..domain.value_objects.token_service import TokenService, default_token_service
from ..models.base import BaseMessage
from .statistics import MessageStatisticsCalculator, MessageStats
from .time_analyzer import TimeAnalyzer
from .tool_analyzer import ToolUsageAnalyzer


@dataclass
class ConversationStats:
    """Comprehensive conversation statistics - aggregates all analyzers."""

    # Message statistics
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    tool_uses: int = 0
    tool_results: int = 0
    errors_count: int = 0

    # Token statistics
    total_tokens: int = 0
    user_tokens: int = 0
    assistant_tokens: int = 0

    # Length statistics
    avg_message_length: float = 0.0
    avg_response_length: float = 0.0

    # Tool statistics
    tools_by_name: Dict[str, int] = field(default_factory=dict)
    tool_success_rates: Dict[str, float] = field(default_factory=dict)

    # Time statistics
    messages_by_hour: Dict[int, int] = field(default_factory=dict)
    messages_by_day: Dict[str, int] = field(default_factory=dict)
    conversation_duration_minutes: float = 0.0
    response_times: List[float] = field(default_factory=list)

    @classmethod
    def from_components(
        cls,
        message_stats: MessageStats,
        time_analyzer: TimeAnalyzer,
        tool_analyzer: ToolUsageAnalyzer,
        token_service: TokenService,
    ) -> "ConversationStats":
        """Create comprehensive stats from component analyzers.

        SOLID: Factory method that composes results from focused analyzers
        """
        return cls(
            # Message stats
            total_messages=message_stats.total_messages,
            user_messages=message_stats.user_messages,
            assistant_messages=message_stats.assistant_messages,
            tool_uses=message_stats.tool_uses,
            tool_results=message_stats.tool_results,
            errors_count=message_stats.errors_count,
            avg_message_length=message_stats.avg_message_length,
            avg_response_length=message_stats.avg_response_length,
            # Tool stats
            tools_by_name=tool_analyzer.get_tool_usage_counts(),
            tool_success_rates=tool_analyzer.calculate_tool_success_rate(),
            # Time stats
            messages_by_hour=time_analyzer.get_hourly_distribution(),
            messages_by_day=time_analyzer.get_daily_distribution(),
            conversation_duration_minutes=time_analyzer.calculate_duration_minutes(),
            response_times=time_analyzer.get_response_times(),
        )


class ConversationAnalytics:
    """Analytics engine for conversations.

    SOLID: Single Responsibility - Conversation analytics only
    DDD: Uses TokenService for token calculations
    95/5: Delegates token counting to unified service

    Example:
        analytics = ConversationAnalytics(conversation)
        stats = analytics.get_statistics()

        print(f"Total messages: {stats.total_messages}")
        print(f"Estimated tokens: {stats.total_tokens}")

        # Get hourly distribution
        hourly = analytics.get_hourly_distribution()
        for hour, count in hourly.items():
            print(f"{hour:02d}:00 - {count} messages")
    """

    def __init__(
        self, conversation: Conversation, token_service: Optional[TokenService] = None
    ):
        """Initialize analytics orchestrator.

        SOLID: Composes focused analyzers instead of doing everything

        Args:
            conversation: The conversation to analyze
            token_service: Service for token calculations, uses default if None
        """
        self.conversation = conversation
        self.token_service = token_service or default_token_service

        # Initialize focused analyzers
        self.message_calculator = MessageStatisticsCalculator(conversation)
        self.time_analyzer = TimeAnalyzer(conversation)
        self.tool_analyzer = ToolUsageAnalyzer(conversation)

        self._stats: Optional[ConversationStats] = None

    def get_statistics(self) -> ConversationStats:
        """Get comprehensive statistics by composing focused analyzers.

        SOLID: Orchestrates specialized services instead of doing work itself

        Returns:
            ConversationStats object with all metrics
        """
        if self._stats is None:
            # Delegate to focused analyzers
            message_stats = self.message_calculator.calculate()

            # Create comprehensive stats from components
            self._stats = ConversationStats.from_components(
                message_stats=message_stats,
                time_analyzer=self.time_analyzer,
                tool_analyzer=self.tool_analyzer,
                token_service=self.token_service,
            )

            # Add token estimates using unified service
            self._add_token_estimates(self._stats)

        return self._stats

    def _add_token_estimates(self, stats: ConversationStats) -> None:
        """Add token estimates to stats using unified service.

        Args:
            stats: Stats object to update with token counts
        """
        total_tokens = 0
        user_tokens = 0
        assistant_tokens = 0

        for msg in self.conversation.messages:
            if msg.text_content:
                token_count = self.token_service.estimate_tokens_rough(msg.text_content)
                total_tokens += token_count

                msg_type = str(msg.type).lower()
                if "user" in msg_type:
                    user_tokens += token_count
                elif "assistant" in msg_type:
                    assistant_tokens += token_count

        stats.total_tokens = total_tokens
        stats.user_tokens = user_tokens
        stats.assistant_tokens = assistant_tokens

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using unified service.

        Delegates to TokenService for consistent estimation.

        Args:
            text: The text to count tokens for

        Returns:
            Estimated token count
        """
        return self.token_service.estimate_tokens_rough(text)

    def get_hourly_distribution(self) -> Dict[int, int]:
        """Get message distribution by hour of day - delegates to TimeAnalyzer."""
        return self.time_analyzer.get_hourly_distribution()

    def get_daily_distribution(self) -> Dict[str, int]:
        """Get message distribution by day - delegates to TimeAnalyzer."""
        return self.time_analyzer.get_daily_distribution()

    def get_tool_usage(self) -> Dict[str, int]:
        """Get tool usage statistics - delegates to ToolUsageAnalyzer."""
        return self.tool_analyzer.get_tool_usage_counts()

    def get_error_messages(self) -> List[BaseMessage]:
        """Get all messages containing errors."""
        return list(self.conversation.with_errors())

    def get_response_times(self) -> List[float]:
        """Calculate response times - delegates to TimeAnalyzer."""
        return self.time_analyzer.get_response_times()

    def get_conversation_duration(self) -> float:
        """Get total conversation duration - delegates to TimeAnalyzer."""
        return self.time_analyzer.calculate_duration_minutes()


class TokenCounter:
    """Utility class for accurate token counting.

    Note: For accurate token counting, install tiktoken:
        pip install tiktoken

    This class provides a fallback estimation if tiktoken
    is not available.
    """

    def __init__(self, model: str = "claude-3"):
        """Initialize token counter.

        Args:
            model: The model to use for tokenization
        """
        self.model = model
        self._encoder = None

        try:
            import tiktoken

            # Try to get encoder for the model
            self._encoder = tiktoken.encoding_for_model("gpt-4")
        except (ImportError, KeyError):
            # Tiktoken not available or model not found
            pass

    def count_tokens(self, text: str) -> int:
        """Count tokens in text.

        Args:
            text: The text to count tokens for

        Returns:
            Token count (exact if tiktoken available, estimate otherwise)
        """
        if self._encoder:
            # Use tiktoken for accurate count
            return len(self._encoder.encode(text))
        else:
            # Fall back to estimation
            return ConversationAnalytics(None).estimate_tokens(text)
