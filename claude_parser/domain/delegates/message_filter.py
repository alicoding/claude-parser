"""
Message filtering delegate.

SOLID: Single Responsibility - Only filtering messages.
95/5: Using toolz for all operations.
"""

from typing import List, Callable, TYPE_CHECKING

from toolz import filter as toolz_filter

if TYPE_CHECKING:
    from ...models import Message, AssistantMessage, UserMessage, Summary
    from ...models.content import ToolUseContent, ToolResultContent


class MessageFilter:
    """
    Handles all message filtering operations.
    Extracted from Conversation to follow SRP.
    """
    
    def __init__(self, messages: List["Message"]):
        """Initialize with messages to filter."""
        self._messages = messages
    
    def by_predicate(self, predicate: Callable) -> List["Message"]:
        """Filter messages using custom predicate."""
        return list(toolz_filter(predicate, self._messages))
    
    def by_type(self, message_type: type) -> List["Message"]:
        """Filter messages by type."""
        return list(toolz_filter(lambda m: isinstance(m, message_type), self._messages))
    
    def assistant_messages(self) -> List["AssistantMessage"]:
        """Get assistant messages."""
        from ...models import AssistantMessage
        return self.by_type(AssistantMessage)
    
    def user_messages(self) -> List["UserMessage"]:
        """Get user messages."""
        from ...models import UserMessage
        return self.by_type(UserMessage)
    
    def summaries(self) -> List["Summary"]:
        """Get summary messages."""
        from ...models import Summary
        return self.by_type(Summary)
    
    def tool_blocks(self) -> List["ToolUseContent | ToolResultContent"]:
        """Get tool use/result content blocks."""
        from ...models.content import ToolResultContent, ToolUseContent
        
        tool_blocks = []
        for msg in self._messages:
            if hasattr(msg, "content_blocks"):
                for block in msg.content_blocks:
                    if isinstance(block, (ToolUseContent, ToolResultContent)):
                        tool_blocks.append(block)
        return tool_blocks
    
    def with_errors(self) -> List["Message"]:
        """Find messages with errors."""
        from ..filters import ErrorFilter
        error_filter = ErrorFilter()
        return self.by_predicate(error_filter.matches)
    
    def containing_text(self, query: str, case_sensitive: bool = False) -> List["Message"]:
        """Filter messages containing specific text."""
        if case_sensitive:
            return self.by_predicate(lambda m: query in m.text_content)
        else:
            query_lower = query.lower()
            return self.by_predicate(lambda m: query_lower in m.text_content.lower())
    
    def by_type_string(self, type_string: str) -> List["Message"]:
        """Filter messages by type string value."""
        return [msg for msg in self._messages if msg.type.value == type_string]