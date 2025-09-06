"""
AdvancedStatsCalculator micro-component - Extended conversation statistics.

95/5 principle: Simple statistics logic, framework handles data structures.
Size: ~18 LOC (LLM-readable in single context)
"""

from typing import List, Dict, Any
from ..core.resources import ResourceManager
from ..models import Message, AssistantMessage, UserMessage
from ..models.content import ToolUseContent, ToolResultContent


class AdvancedStatsCalculator:
    """Micro-component: Calculate advanced conversation statistics."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def calculate_extended_stats(self, messages: List[Message]) -> Dict[str, Any]:
        """Calculate extended statistics - simple Python logic."""
        total_length = sum(len(msg.text_content) if msg.text_content else 0 for msg in messages)
        user_msgs = [m for m in messages if isinstance(m, UserMessage)]
        assistant_msgs = [m for m in messages if isinstance(m, AssistantMessage)]

        # Count tools
        tool_uses = tool_results = errors = 0
        for msg in assistant_msgs:
            if hasattr(msg, 'content_blocks'):
                for block in msg.content_blocks:
                    if isinstance(block, ToolUseContent):
                        tool_uses += 1
                    elif isinstance(block, ToolResultContent):
                        tool_results += 1
            if msg.text_content and ('error' in msg.text_content.lower() or 'exception' in msg.text_content.lower()):
                errors += 1

        return {
            'tool_uses': tool_uses,
            'tool_results': tool_results,
            'errors_count': errors,
            'avg_message_length': total_length / len(messages) if messages else 0,
            'avg_response_length': sum(len(m.text_content) if m.text_content else 0 for m in assistant_msgs) / len(assistant_msgs) if assistant_msgs else 0,
        }
