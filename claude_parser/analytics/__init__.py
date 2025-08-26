"""Analytics engine for Claude Parser.

Provides token counting, aggregations, and visualizations
for Claude conversations.

Example:
    from claude_parser import load
    from claude_parser.analytics import ConversationAnalytics

    conv = load("conversation.jsonl")
    analytics = ConversationAnalytics(conv)

    # Get token counts
    stats = analytics.get_statistics()
    print(f"Total tokens: {stats['total_tokens']}")
"""

from .analyzer import ConversationAnalytics, ConversationStats
from .statistics import MessageStatisticsCalculator, MessageStats
from .time_analyzer import TimeAnalyzer
from .tool_analyzer import ToolUsageAnalyzer

__all__ = [
    "ConversationAnalytics",
    "ConversationStats",
    "MessageStats",
    "MessageStatisticsCalculator",
    "TimeAnalyzer",
    "ToolUsageAnalyzer",
]
