"""
Analytics analyzer - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from ..core.resources import get_resource_manager
from ..components.message_counter import MessageCounter
from ..components.stats_calculator import StatsCalculator
from ..components.advanced_stats_calculator import AdvancedStatsCalculator
from ..components.time_analyzer import TimeAnalyzer as TimeAnalyzerComponent
from ..components.tool_analyzer import ToolAnalyzer as ToolAnalyzerComponent
from ..domain.entities.conversation import Conversation


@dataclass
class ConversationStats:
    """Simple conversation statistics - using micro-components."""

    # Basic statistics
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    message_types: Dict[str, int] = field(default_factory=dict)


class ConversationAnalytics:
    """Clean analytics service using ResourceManager pattern."""

    def __init__(self, conversation: Conversation):
        """Initialize with conversation and centralized resources."""
        self.conversation = conversation
        self.resources = get_resource_manager()

        # Initialize micro-components
        self.message_counter = MessageCounter(self.resources)
        self.stats_calculator = StatsCalculator(self.resources)
        self.advanced_stats = AdvancedStatsCalculator(self.resources)
        self.time_analyzer = TimeAnalyzerComponent(self.resources)
        self.tool_analyzer = ToolAnalyzerComponent(self.resources)

        from ..components.token_counter import TokenCounter as TokenCounterComponent
        self.token_counter = TokenCounterComponent(self.resources)

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics using micro-components."""
        # Use micro-components for calculations
        basic_stats = self.stats_calculator.calculate_basic_stats(self.conversation.messages)
        type_counts = self.message_counter.count_by_type(self.conversation.messages)
        extended_stats = self.advanced_stats.calculate_extended_stats(self.conversation.messages)

        # Combine results
        return {
            **basic_stats,
            **extended_stats,
            'message_types': type_counts,
        }

    def get_time_analysis(self) -> Dict[str, Any]:
        """Get time analysis using micro-component."""
        return self.time_analyzer.analyze_time_patterns(self.conversation.messages)

    def get_tool_analysis(self) -> Dict[str, Any]:
        """Get tool analysis using micro-component."""
        return self.tool_analyzer.analyze_tool_usage(self.conversation.messages)


# Backward Compatibility Classes

class TokenCounter:
    """Token counter for backward compatibility."""

    def __init__(self):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        from ..components.token_counter import TokenCounter as TokenCounterComponent
        self._counter = TokenCounterComponent(self.resources)

    def count_tokens(self, text: str) -> int:
        """Count tokens using micro-component."""
        return self._counter.count(text)


class MessageStatisticsCalculator:
    """Backward compatibility for legacy MessageStatisticsCalculator."""

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.analytics = ConversationAnalytics(conversation)

    def calculate(self):
        """Calculate statistics - redirect to new implementation."""
        stats = self.analytics.get_statistics()
        # Convert to legacy format
        from dataclasses import dataclass

        @dataclass
        class MessageStats:
            total_messages: int = 0
            user_messages: int = 0
            assistant_messages: int = 0
            tool_uses: int = 0
            tool_results: int = 0
            errors_count: int = 0
            avg_message_length: float = 0.0
            avg_response_length: float = 0.0

        return MessageStats(
            total_messages=stats.get('total_messages', 0),
            user_messages=stats.get('user_messages', 0),
            assistant_messages=stats.get('assistant_messages', 0),
            tool_uses=stats.get('tool_uses', 0),
            tool_results=stats.get('tool_results', 0),
            errors_count=stats.get('errors_count', 0),
            avg_message_length=stats.get('avg_message_length', 0.0),
            avg_response_length=stats.get('avg_response_length', 0.0),
        )


class TimeAnalyzer:
    """Backward compatibility for legacy TimeAnalyzer."""

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.analytics = ConversationAnalytics(conversation)

    def get_hourly_distribution(self) -> Dict[int, int]:
        """Get hourly distribution."""
        return self.analytics.get_time_analysis().get('hourly_distribution', {})

    def get_daily_distribution(self) -> Dict[str, int]:
        """Get daily distribution."""
        return self.analytics.get_time_analysis().get('daily_distribution', {})

    def calculate_duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.analytics.get_time_analysis().get('duration_minutes', 0.0)

    def get_response_times(self) -> List[float]:
        """Get response times."""
        return self.analytics.get_time_analysis().get('response_times', [])

    def get_peak_hours(self, limit: int = 3) -> List[int]:
        """Get peak hours."""
        peak_hours = self.analytics.get_time_analysis().get('peak_hours', [])
        return [hour for hour, count in peak_hours[:limit]]


class ToolUsageAnalyzer:
    """Backward compatibility for legacy ToolUsageAnalyzer."""

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.analytics = ConversationAnalytics(conversation)

    def get_tool_usage_counts(self) -> Dict[str, int]:
        """Get tool usage counts."""
        return self.analytics.get_tool_analysis().get('tool_usage_counts', {})

    def get_most_used_tools(self, limit: int = 5) -> List[tuple]:
        """Get most used tools."""
        most_used = self.analytics.get_tool_analysis().get('most_used_tools', [])
        return most_used[:limit]
