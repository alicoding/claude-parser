"""
Token analyzer service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from typing import Dict, Any, Optional
from ...core.resources import get_resource_manager
from ...components.token_usage_analyzer import TokenUsageAnalyzer, TokenStats
from ...domain.entities.conversation import Conversation


class TokenAnalyzerService:
    """Clean token analyzer service using ResourceManager pattern."""

    def __init__(self):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        self.usage_analyzer = TokenUsageAnalyzer(self.resources)

    def analyze_conversation(self, conversation: Conversation) -> TokenStats:
        """Analyze token usage in conversation using micro-component."""
        return self.usage_analyzer.analyze_usage(conversation.messages)

    def analyze_session_tokens(self, transcript_path: str) -> Dict[str, Any]:
        """Analyze token usage for entire session."""
        from ...application.conversation_service import load
        conversation = load(transcript_path)
        stats = self.analyze_conversation(conversation)

        return {
            'total_tokens': stats.total_tokens,
            'input_tokens': stats.total_input,
            'output_tokens': stats.total_output,
            'cache_tokens': stats.total_cache_read,
            'cache_hit_rate': stats.cache_hit_rate,
            'message_count': stats.message_count,
        }


# Backward Compatibility Class
class TokenAnalyzer:
    """Backward compatibility for legacy TokenAnalyzer."""

    def __init__(self, token_service: Optional[Any] = None):
        """Initialize with service (token_service ignored - using ResourceManager now)."""
        self.service = TokenAnalyzerService()

    def analyze_conversation(self, conversation: Conversation) -> TokenStats:
        """Analyze conversation - redirect to new implementation."""
        return self.service.analyze_conversation(conversation)

    def analyze_session_tokens(self, transcript_path: str) -> Dict[str, Any]:
        """Analyze session tokens - redirect to new implementation."""
        return self.service.analyze_session_tokens(transcript_path)
