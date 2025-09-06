"""
Tool usage analysis for conversations - SOLID Single Responsibility.

Focused solely on tool usage patterns and statistics.
"""

from typing import Dict, List, Tuple
from collections import defaultdict

from ..domain.entities.conversation import Conversation
from ..models.content import ToolUseContent, ToolResultContent


class ToolUsageAnalyzer:
    """Analyzes tool usage patterns in conversations.

    SOLID: Single Responsibility - Only tool usage analysis
    """

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.conversation = conversation

    def get_tool_usage_counts(self) -> Dict[str, int]:
        """Get usage count for each tool.

        Returns:
            Dictionary mapping tool name to usage count
        """
        tool_counts = defaultdict(int)

        # Extract tool uses from conversation
        for tool_use in self.conversation.tool_uses:
            if isinstance(tool_use, ToolUseContent):
                tool_name = tool_use.name
                tool_counts[tool_name] += 1

        return dict(tool_counts)

    def get_most_used_tools(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get the most frequently used tools.

        Args:
            limit: Number of top tools to return

        Returns:
            List of (tool_name, count) tuples, sorted by usage
        """
        tool_counts = self.get_tool_usage_counts()

        # Sort by count, descending
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)

        return sorted_tools[:limit]

    def calculate_tool_success_rate(self) -> Dict[str, float]:
        """Calculate success rate for each tool.

        Success is measured as tool_result following tool_use without error.

        Returns:
            Dictionary mapping tool name to success rate (0.0-1.0)
        """
        tool_attempts = defaultdict(int)
        tool_successes = defaultdict(int)

        # Track tool use and result pairs
        messages = self.conversation.messages

        for i, msg in enumerate(messages):
            if hasattr(msg, 'content_blocks'):
                for block in msg.content_blocks:
                    if isinstance(block, ToolUseContent):
                        tool_name = block.name
                        tool_attempts[tool_name] += 1

                        # Look for corresponding result in next few messages
                        for j in range(i + 1, min(i + 3, len(messages))):
                            next_msg = messages[j]
                            if hasattr(next_msg, 'content_blocks'):
                                for next_block in next_msg.content_blocks:
                                    if (isinstance(next_block, ToolResultContent) and
                                        hasattr(next_block, 'tool_use_id') and
                                        hasattr(block, 'id') and
                                        next_block.tool_use_id == block.id):

                                        # Check if result indicates success
                                        if not self._is_error_result(next_block):
                                            tool_successes[tool_name] += 1
                                        break

        # Calculate success rates
        success_rates = {}
        for tool_name, attempts in tool_attempts.items():
            if attempts > 0:
                success_rates[tool_name] = tool_successes[tool_name] / attempts
            else:
                success_rates[tool_name] = 0.0

        return success_rates

    def get_tool_usage_timeline(self) -> List[Dict[str, any]]:
        """Get timeline of tool usage.

        Returns:
            List of tool usage events with timestamps
        """
        timeline = []

        for msg in self.conversation.messages:
            if hasattr(msg, 'content_blocks') and msg.parsed_timestamp:
                for block in msg.content_blocks:
                    if isinstance(block, ToolUseContent):
                        timeline.append({
                            'timestamp': msg.parsed_timestamp,
                            'tool_name': block.name,
                            'type': 'tool_use',
                            'input_preview': str(block.input)[:100] if block.input else ""
                        })
                    elif isinstance(block, ToolResultContent):
                        timeline.append({
                            'timestamp': msg.parsed_timestamp,
                            'tool_name': getattr(block, 'tool_name', 'unknown'),
                            'type': 'tool_result',
                            'success': not self._is_error_result(block)
                        })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        return timeline

    def _is_error_result(self, tool_result: ToolResultContent) -> bool:
        """Check if a tool result indicates an error.

        Args:
            tool_result: The tool result to check

        Returns:
            True if result appears to be an error
        """
        if not tool_result.content:
            return False

        # Check for common error indicators
        content_str = str(tool_result.content).lower()
        error_indicators = [
            'error', 'exception', 'failed', 'denied',
            'invalid', 'not found', 'permission denied'
        ]

        return any(indicator in content_str for indicator in error_indicators)


__all__ = ["ToolUsageAnalyzer"]
