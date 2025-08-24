"""Tests for domain conversation module."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from claude_parser.domain.conversation import (
    ConversationAnalyzer,
    ContentFilter,
    TypeFilter,
    ErrorFilter,
)
from claude_parser.models import UserMessage, AssistantMessage, MessageType


class TestConversationAnalyzer:
    """Test ConversationAnalyzer domain service."""
    
    def test_analyzer_init(self):
        """Test analyzer initialization."""
        mock_conv = MagicMock()
        analyzer = ConversationAnalyzer(mock_conv)
        
        assert analyzer.conversation == mock_conv
    
    def test_get_stats(self):
        """Test getting conversation statistics."""
        mock_conv = MagicMock()
        mock_conv.__len__ = MagicMock(return_value=100)
        mock_conv.assistant_messages = [MagicMock()] * 50
        mock_conv.user_messages = [MagicMock()] * 45
        mock_conv.tool_uses = [MagicMock()] * 5
        mock_conv.with_errors = MagicMock(return_value=[])
        mock_conv.session_id = "test-session"
        mock_conv.summaries = []
        
        analyzer = ConversationAnalyzer(mock_conv)
        stats = analyzer.get_stats()
        
        assert stats["total_messages"] == 100
        assert stats["assistant_messages"] == 50
        assert stats["user_messages"] == 45
        assert stats["tool_uses"] == 5
        assert stats["error_messages"] == 0
        assert stats["session_id"] == "test-session"
        assert stats["has_summaries"] is False


class TestMessageFilters:
    """Test message filter strategies."""
    
    def test_content_filter_case_insensitive(self):
        """Test content filter with case insensitive search."""
        filter = ContentFilter("hello", case_sensitive=False)
        
        msg1 = MagicMock()
        msg1.text_content = "Hello World"
        assert filter.matches(msg1) is True
        
        msg2 = MagicMock()
        msg2.text_content = "goodbye"
        assert filter.matches(msg2) is False
    
    def test_content_filter_case_sensitive(self):
        """Test content filter with case sensitive search."""
        filter = ContentFilter("Hello", case_sensitive=True)
        
        msg1 = MagicMock()
        msg1.text_content = "Hello World"
        assert filter.matches(msg1) is True
        
        msg2 = MagicMock()
        msg2.text_content = "hello world"
        assert filter.matches(msg2) is False
    
    def test_type_filter(self):
        """Test type filter."""
        filter = TypeFilter(UserMessage)
        
        user_msg = UserMessage(
            type=MessageType.USER,
            content="test"
        )
        assert filter.matches(user_msg) is True
        
        assistant_msg = AssistantMessage(
            type=MessageType.ASSISTANT,
            content="response"
        )
        assert filter.matches(assistant_msg) is False
    
    def test_error_filter(self):
        """Test error filter."""
        filter = ErrorFilter()
        
        error_msg = MagicMock()
        error_msg.text_content = "An error occurred"
        assert filter.matches(error_msg) is True
        
        normal_msg = MagicMock()
        normal_msg.text_content = "Everything is fine"
        assert filter.matches(normal_msg) is False
        
        exception_msg = MagicMock()
        exception_msg.text_content = "Exception: Something went wrong"
        assert filter.matches(exception_msg) is True