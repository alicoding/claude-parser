"""
Session analyzer - Handles session boundaries and current session token counting.

SOLID: Single Responsibility - Session analysis only
95/5: Uses tiktoken for token counting
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass
import tiktoken
from toolz import pipe, map, filter as toolz_filter, reduce

from claude_parser.models.usage import UsageInfo


@dataclass
class SessionStats:
    """Statistics for current session only."""
    
    session_start_index: int = 0
    message_count: int = 0
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_created_tokens: int = 0
    cache_hit_rate: float = 0.0
    cost_usd: float = 0.0
    model: str = "unknown"
    context_limit: int = 200000  # Default for Claude


class SessionAnalyzer:
    """Analyzes current session, not entire transcript.
    
    A session is defined as messages after the most recent summary.
    """
    
    # Claude 3.5 Sonnet pricing per 1M tokens
    PRICING = {
        "input": 3.00,
        "output": 15.00,
        "cache_write": 3.75,
        "cache_read": 0.30,
    }
    
    def __init__(self):
        """Initialize session analyzer."""
        # Use cl100k_base as approximation for Claude
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def find_current_session_start(self, conversation) -> int:
        """Find where current session starts.
        
        Session starts after the last compact summary message.
        
        Args:
            conversation: Conversation object
            
        Returns:
            Index where current session starts
        """
        # Find last summary using functional approach
        def is_summary(indexed_msg):
            i, msg = indexed_msg
            if hasattr(msg, 'is_compact_summary') and msg.is_compact_summary:
                return True
            if hasattr(msg, 'raw_data') and msg.raw_data.get('isCompactSummary'):
                return True
            return False
        
        # Get all summary indices
        summary_indices = list(toolz.pipe(
            enumerate(conversation.messages),
            toolz.filter(is_summary),
            toolz.map(lambda x: x[0])
        ))
        
        # Session starts after last summary (or at 0 if no summary)
        last_summary_index = summary_indices[-1] if summary_indices else -1
        return last_summary_index + 1 if last_summary_index >= 0 else 0
    
    def analyze_current_session(self, conversation) -> SessionStats:
        """Analyze only the current session's token usage.
        
        Args:
            conversation: Full conversation object
            
        Returns:
            SessionStats for current session only
        """
        stats = SessionStats()
        
        # Find session boundary
        stats.session_start_index = self.find_current_session_start(conversation)
        
        # Get messages in current session
        session_messages = conversation.messages[stats.session_start_index:]
        stats.message_count = len(session_messages)
        
        # Get the LATEST assistant message's token usage (not sum!)
        # Each usage field represents the total context at that point
        def get_usage(msg):
            if str(msg.type).lower().endswith("assistant"):
                if hasattr(msg, 'message') and isinstance(msg.message, dict):
                    usage_data = msg.message.get('usage', {})
                    if usage_data:
                        return usage_data
            return None
        
        # Find first assistant message with usage (from end)
        latest_usage = toolz.pipe(
            reversed(session_messages),
            toolz.map(get_usage),
            toolz.filter(lambda x: x is not None),
            toolz.take(1),
            list
        )
        latest_usage = latest_usage[0] if latest_usage else None
        
        if latest_usage:
            # Use the latest token count - this is the current context size
            stats.input_tokens = latest_usage.get('input_tokens', 0)
            stats.output_tokens = latest_usage.get('output_tokens', 0)
            stats.cache_read_tokens = latest_usage.get('cache_read_input_tokens', 0)
            stats.cache_created_tokens = latest_usage.get('cache_creation_input_tokens', 0)
            
            # Get model info from the message that had usage
            def get_model_info(msg):
                if str(msg.type).lower().endswith("assistant"):
                    if hasattr(msg, 'message') and isinstance(msg.message, dict):
                        if msg.message.get('usage'):
                            return msg.message.get('model', 'unknown')
                return None
            
            # Find first assistant message with model info
            model_info = toolz.pipe(
                reversed(session_messages),
                toolz.map(get_model_info),
                toolz.filter(lambda x: x is not None),
                toolz.take(1),
                list
            )
            
            if model_info:
                stats.model = model_info[0]
                # Set context limit based on model
                if 'opus' in stats.model.lower():
                    stats.context_limit = 200000  # Opus 4.1: 200K
                elif 'sonnet' in stats.model.lower():
                    # Could be 200K or 1M, default to 200K
                    stats.context_limit = 200000
        
        # Calculate total
        stats.total_tokens = (
            stats.input_tokens +
            stats.output_tokens +
            stats.cache_read_tokens +
            stats.cache_created_tokens
        )
        
        # Calculate cache hit rate
        total_input = stats.input_tokens + stats.cache_read_tokens
        if total_input > 0:
            stats.cache_hit_rate = stats.cache_read_tokens / total_input
        
        # Calculate cost
        stats.cost_usd = self._calculate_cost(stats)
        
        return stats
    
    def get_tokens_since_last_reinject(self, conversation, reinject_interval: int = 25000) -> Tuple[int, bool]:
        """Get tokens since last reinject point.
        
        Args:
            conversation: Conversation object
            reinject_interval: Token interval for reinjection
            
        Returns:
            Tuple of (tokens_since_reinject, should_reinject)
        """
        stats = self.analyze_current_session(conversation)
        tokens_since = stats.total_tokens % reinject_interval
        should_reinject = stats.total_tokens > 0 and tokens_since < 1000  # Within 1K of milestone
        
        return tokens_since, should_reinject
    
    def estimate_tokens_for_text(self, text: str) -> int:
        """Estimate token count for text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        return len(self.encoder.encode(text))
    
    def _calculate_cost(self, stats: SessionStats) -> float:
        """Calculate USD cost for session.
        
        Args:
            stats: Session statistics
            
        Returns:
            Cost in USD
        """
        cost = 0.0
        
        # Convert to millions for pricing
        cost += (stats.input_tokens / 1_000_000) * self.PRICING["input"]
        cost += (stats.output_tokens / 1_000_000) * self.PRICING["output"]
        cost += (stats.cache_created_tokens / 1_000_000) * self.PRICING["cache_write"]
        cost += (stats.cache_read_tokens / 1_000_000) * self.PRICING["cache_read"]
        
        return round(cost, 4)
    
    def format_session_banner(self, stats: SessionStats) -> str:
        """Format concise session stats for display.
        
        Args:
            stats: Session statistics
            
        Returns:
            Formatted banner string with percentage remaining
        """
        # Calculate percentage used
        percent_used = (stats.total_tokens / stats.context_limit * 100) if stats.context_limit > 0 else 0
        
        # Add emoji based on usage
        if percent_used < 50:
            emoji = "🟢"
        elif percent_used < 75:
            emoji = "🟡"
        elif percent_used < 90:
            emoji = "🟠"
        else:
            emoji = "🔴"
        
        return (
            f"📊 {stats.total_tokens:,}/{stats.context_limit:,} tokens "
            f"({percent_used:.0f}% used) {emoji} | "
            f"Cache: {stats.cache_hit_rate:.0%} | "
            f"${stats.cost_usd:.2f}"
        )


# Export main classes
__all__ = ["SessionAnalyzer", "SessionStats"]