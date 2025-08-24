"""
Conversation analysis service.

SOLID: Single Responsibility - Only analysis operations.
DDD: Domain Service - Stateless operations on aggregates.
"""

from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from ..entities.conversation import Conversation


class ConversationAnalyzer:
    """Domain service for conversation analysis."""
    
    def __init__(self, conversation: 'Conversation'):
        """Initialize analyzer with a conversation."""
        self.conversation = conversation
    
    def get_stats(self) -> Dict[str, Any]:
        """Generate conversation statistics and insights."""
        return {
            'total_messages': len(self.conversation),
            'assistant_messages': len(self.conversation.assistant_messages),
            'user_messages': len(self.conversation.user_messages),
            'tool_uses': len(self.conversation.tool_uses),
            'error_messages': len(self.conversation.with_errors()),
            'session_id': self.conversation.session_id,
            'has_summaries': len(self.conversation.summaries) > 0
        }