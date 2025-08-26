"""
Conversation statistics calculation - SOLID Single Responsibility.

Focused solely on calculating message counts and basic stats.
"""

from dataclasses import dataclass

from ..domain.entities.conversation import Conversation
from ..models import AssistantMessage, UserMessage
from ..models.content import ToolResultContent, ToolUseContent


@dataclass
class MessageStats:
    """Basic message statistics."""

    total_messages: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    tool_uses: int = 0
    tool_results: int = 0
    errors_count: int = 0

    avg_message_length: float = 0.0
    avg_response_length: float = 0.0


class MessageStatisticsCalculator:
    """Calculates basic message statistics.

    SOLID: Single Responsibility - Only message counting and basic stats
    """

    def __init__(self, conversation: Conversation):
        """Initialize with conversation."""
        self.conversation = conversation

    def calculate(self) -> MessageStats:
        """Calculate basic message statistics.

        Returns:
            MessageStats with counts and averages
        """
        stats = MessageStats()
        total_length = 0
        response_length = 0

        for msg in self.conversation.messages:
            stats.total_messages += 1
            message_length = len(msg.text_content) if msg.text_content else 0
            total_length += message_length

            if isinstance(msg, UserMessage):
                stats.user_messages += 1
            elif isinstance(msg, AssistantMessage):
                stats.assistant_messages += 1
                response_length += message_length

                # Count tool usage in content
                if hasattr(msg, "content_blocks"):
                    for block in msg.content_blocks:
                        if isinstance(block, ToolUseContent):
                            stats.tool_uses += 1
                        elif isinstance(block, ToolResultContent):
                            stats.tool_results += 1

            # Check for errors (simple pattern matching)
            if msg.text_content and (
                "error" in msg.text_content.lower()
                or "exception" in msg.text_content.lower()
            ):
                stats.errors_count += 1

        # Calculate averages
        if stats.total_messages > 0:
            stats.avg_message_length = total_length / stats.total_messages

        if stats.assistant_messages > 0:
            stats.avg_response_length = response_length / stats.assistant_messages

        return stats


__all__ = ["MessageStats", "MessageStatisticsCalculator"]
