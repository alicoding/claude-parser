"""Analytics analyzer for conversations.

Provides detailed analytics including token counting,
message statistics, and usage patterns.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import re

from ..domain.conversation import Conversation
from ..models import Message, AssistantMessage, UserMessage, ToolUse, ToolResult


@dataclass
class ConversationStats:
    """Statistics for a conversation."""
    
    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    tool_uses: int = 0
    tool_results: int = 0
    
    total_tokens: int = 0
    user_tokens: int = 0
    assistant_tokens: int = 0
    
    avg_message_length: float = 0.0
    avg_response_length: float = 0.0
    
    tools_by_name: Dict[str, int] = field(default_factory=dict)
    messages_by_hour: Dict[int, int] = field(default_factory=dict)
    messages_by_day: Dict[str, int] = field(default_factory=dict)
    
    errors_count: int = 0
    conversation_duration_minutes: float = 0.0


class ConversationAnalytics:
    """Analytics engine for conversations.
    
    Provides comprehensive analytics including token counting,
    message statistics, tool usage patterns, and more.
    
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
    
    # Rough token estimation (4 chars per token average)
    CHARS_PER_TOKEN = 4
    
    def __init__(self, conversation: Conversation):
        """Initialize analytics for a conversation.
        
        Args:
            conversation: The conversation to analyze
        """
        self.conversation = conversation
        self._stats: Optional[ConversationStats] = None
    
    def get_statistics(self) -> ConversationStats:
        """Get comprehensive statistics for the conversation.
        
        Returns:
            ConversationStats object with all metrics
        """
        if self._stats is None:
            self._calculate_statistics()
        return self._stats
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text.
        
        Uses a simple heuristic of ~4 characters per token.
        For accurate counts, use tiktoken library.
        
        Args:
            text: The text to count tokens for
            
        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 chars per token
        # Adjust for whitespace and punctuation
        words = text.split()
        
        # Rough estimation
        char_count = len(text)
        word_count = len(words)
        
        # Average between character and word-based estimates
        char_estimate = char_count / self.CHARS_PER_TOKEN
        word_estimate = word_count * 1.3  # Words are ~1.3 tokens on average
        
        return int((char_estimate + word_estimate) / 2)
    
    def get_hourly_distribution(self) -> Dict[int, int]:
        """Get message distribution by hour of day.
        
        Returns:
            Dictionary mapping hour (0-23) to message count
        """
        distribution = defaultdict(int)
        
        for msg in self.conversation.messages:
            if msg.parsed_timestamp:
                hour = msg.parsed_timestamp.hour
                distribution[hour] += 1
        
        return dict(distribution)
    
    def get_daily_distribution(self) -> Dict[str, int]:
        """Get message distribution by day.
        
        Returns:
            Dictionary mapping date string to message count
        """
        distribution = defaultdict(int)
        
        for msg in self.conversation.messages:
            if msg.parsed_timestamp:
                day = msg.parsed_timestamp.date().isoformat()
                distribution[day] += 1
        
        return dict(distribution)
    
    def get_tool_usage(self) -> Dict[str, int]:
        """Get tool usage statistics.
        
        Returns:
            Dictionary mapping tool name to usage count
        """
        tool_usage = defaultdict(int)
        
        for msg in self.conversation.tool_uses:
            if isinstance(msg, ToolUse):
                tool_usage[msg.tool_name] += 1
        
        return dict(tool_usage)
    
    def get_error_messages(self) -> List[Message]:
        """Get all messages containing errors.
        
        Returns:
            List of messages with errors
        """
        return list(self.conversation.with_errors())
    
    def get_response_times(self) -> List[float]:
        """Calculate response times between user and assistant messages.
        
        Returns:
            List of response times in seconds
        """
        response_times = []
        user_messages = list(self.conversation.user_messages)
        assistant_messages = list(self.conversation.assistant_messages)
        
        for user_msg in user_messages:
            user_time = user_msg.parsed_timestamp
            if not user_time:
                continue
            
            # Find next assistant message
            for assistant_msg in assistant_messages:
                assistant_time = assistant_msg.parsed_timestamp
                if assistant_time and assistant_time > user_time:
                    response_time = (assistant_time - user_time).total_seconds()
                    response_times.append(response_time)
                    break
        
        return response_times
    
    def get_conversation_duration(self) -> float:
        """Get total conversation duration in minutes.
        
        Returns:
            Duration in minutes
        """
        if not self.conversation.messages:
            return 0.0
        
        timestamps = [
            msg.parsed_timestamp 
            for msg in self.conversation.messages 
            if msg.parsed_timestamp
        ]
        
        if len(timestamps) < 2:
            return 0.0
        
        duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
        return duration
    
    def _calculate_statistics(self) -> None:
        """Calculate all statistics for the conversation."""
        stats = ConversationStats()
        
        # Message counts
        stats.total_messages = len(self.conversation)
        stats.user_messages = len(list(self.conversation.user_messages))
        stats.assistant_messages = len(list(self.conversation.assistant_messages))
        
        # Count tool uses and results from the combined property
        tool_messages = list(self.conversation.tool_uses)
        stats.tool_uses = sum(1 for m in tool_messages if isinstance(m, ToolUse))
        stats.tool_results = sum(1 for m in tool_messages if isinstance(m, ToolResult))
        
        # Token estimates
        total_chars = 0
        user_chars = 0
        assistant_chars = 0
        
        for msg in self.conversation.messages:
            text = msg.text_content
            char_count = len(text) if text else 0
            total_chars += char_count
            
            if isinstance(msg, UserMessage):
                user_chars += char_count
            elif isinstance(msg, AssistantMessage):
                assistant_chars += char_count
        
        stats.total_tokens = self.estimate_tokens(str(total_chars))
        stats.user_tokens = self.estimate_tokens(str(user_chars))
        stats.assistant_tokens = self.estimate_tokens(str(assistant_chars))
        
        # Average lengths
        if stats.user_messages > 0:
            stats.avg_message_length = user_chars / stats.user_messages
        
        if stats.assistant_messages > 0:
            stats.avg_response_length = assistant_chars / stats.assistant_messages
        
        # Tool usage
        stats.tools_by_name = self.get_tool_usage()
        
        # Time distributions
        stats.messages_by_hour = self.get_hourly_distribution()
        stats.messages_by_day = self.get_daily_distribution()
        
        # Errors
        stats.errors_count = len(self.get_error_messages())
        
        # Duration
        stats.conversation_duration_minutes = self.get_conversation_duration()
        
        self._stats = stats


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