"""
Analytics Domain: Conversation statistics and analysis

Tests 95% use case analytics functions - interface only.
"""

from claude_parser.analytics import (
    ConversationAnalytics, ConversationStats, MessageStatisticsCalculator,
    MessageStats, TimeAnalyzer, ToolUsageAnalyzer
)
from claude_parser import load
from ..framework import EnforcedTestBase, get_real_claude_transcript


class TestAnalyticsFeatures(EnforcedTestBase):
    """Test analytics features - conversation analysis."""

    def test_conversation_analytics_interface_contract(self):
        """Interface: ConversationAnalytics() accepts conversation, has methods."""
        # Interface contract - class exists and has methods
        assert callable(ConversationAnalytics)

        # Test constructor signature
        from inspect import signature
        sig = signature(ConversationAnalytics.__init__)
        assert 'conversation' in sig.parameters

    def test_analytics_methods_exist(self):
        """Interface: Analytics has all expected public methods."""
        # Verify public interface exists
        assert hasattr(ConversationAnalytics, 'get_statistics')
        assert hasattr(ConversationAnalytics, 'get_hourly_distribution')
        assert hasattr(ConversationAnalytics, 'get_tool_usage')
        assert callable(getattr(ConversationAnalytics, 'get_statistics'))
