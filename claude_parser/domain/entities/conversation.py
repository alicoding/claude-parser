"""
Conversation entity - Core domain model.

SOLID: Single Responsibility - ONLY conversation representation.
DDD: Entity with identity (session_id).
95/5: Using toolz for all filtering operations.
"""

from typing import List, Optional, Iterator
from toolz import filter as toolz_filter

from ...models import Message, AssistantMessage, UserMessage, ToolUse, ToolResult, Summary
from ..value_objects.metadata import ConversationMetadata
from ..filters import ErrorFilter


class Conversation:
    """
    Conversation aggregate root.
    Clean, focused entity following SOLID principles.
    All navigation/analysis extracted to services.
    """
    
    def __init__(self, messages: List[Message], metadata: ConversationMetadata):
        """Initialize conversation with messages and metadata."""
        self._messages = messages
        self._metadata = metadata
    
    # Core Properties
    @property
    def metadata(self) -> ConversationMetadata:
        """Get conversation metadata."""
        return self._metadata
    
    @property
    def session_id(self) -> Optional[str]:
        """Get session ID."""
        return self._metadata.session_id
    
    @property
    def filepath(self):
        """Get filepath from metadata."""
        return self._metadata.filepath
    
    @property
    def current_dir(self) -> Optional[str]:
        """Get current directory from metadata."""
        return self._metadata.current_dir
    
    @property
    def git_branch(self) -> Optional[str]:
        """Get git branch from metadata."""
        return self._metadata.git_branch
    
    @property
    def messages(self) -> List[Message]:
        """Get all messages (immutable view)."""
        return self._messages.copy()
    
    @property
    def assistant_messages(self) -> List[AssistantMessage]:
        """Get assistant messages using toolz."""
        return list(toolz_filter(
            lambda m: isinstance(m, AssistantMessage),
            self._messages
        ))
    
    @property
    def user_messages(self) -> List[UserMessage]:
        """Get user messages using toolz."""
        return list(toolz_filter(
            lambda m: isinstance(m, UserMessage),
            self._messages
        ))
    
    @property
    def tool_uses(self) -> List[ToolUse | ToolResult]:
        """Get tool messages using toolz."""
        return list(toolz_filter(
            lambda m: isinstance(m, (ToolUse, ToolResult)),
            self._messages
        ))
    
    @property
    def summaries(self) -> List[Summary]:
        """Get summaries using toolz."""
        return list(toolz_filter(
            lambda m: isinstance(m, Summary),
            self._messages
        ))
    
    # Simple query methods
    def filter_messages(self, predicate) -> List[Message]:
        """Filter messages using custom predicate."""
        return list(toolz_filter(predicate, self._messages))
    
    def search(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """Search messages containing text."""
        if case_sensitive:
            return self.filter_messages(
                lambda m: query in m.text_content
            )
        else:
            query_lower = query.lower()
            return self.filter_messages(
                lambda m: query_lower in m.text_content.lower()
            )
    
    def filter(self, predicate) -> List[Message]:
        """Alias for filter_messages for backward compatibility."""
        return self.filter_messages(predicate)
    
    def with_errors(self) -> List[Message]:
        """Find messages with errors."""
        error_filter = ErrorFilter()
        return self.filter_messages(error_filter.matches)
    
    def before_summary(self, limit: int = 10) -> List[Message]:
        """Get messages before the last summary."""
        # Find last summary index
        summary_indices = [
            i for i, msg in enumerate(self._messages) 
            if isinstance(msg, Summary)
        ]
        
        if not summary_indices:
            # No summary, return last 'limit' messages
            return self._messages[-limit:] if limit < len(self._messages) else self._messages[:]
        
        # Get messages before last summary
        last_summary_idx = summary_indices[-1]
        start_idx = max(0, last_summary_idx - limit)
        return self._messages[start_idx:last_summary_idx]
    
    # Alias methods for backward compatibility
    def tool_messages(self) -> List[ToolUse | ToolResult]:
        """Alias for tool_uses property for backward compatibility."""
        return self.tool_uses
    
    def messages_with_errors(self) -> List[Message]:
        """Alias for with_errors() for backward compatibility."""
        return self.with_errors()
    
    def messages_before_summary(self, limit: int = 10) -> List[Message]:
        """Alias for before_summary() for backward compatibility."""
        return self.before_summary(limit)
    
    # Collection interface
    def __len__(self) -> int:
        """Get number of messages."""
        return len(self._messages)
    
    def __getitem__(self, index: int | slice) -> Message | List[Message]:
        """Get message by index or slice."""
        return self._messages[index]
    
    def __iter__(self) -> Iterator[Message]:
        """Iterate over messages."""
        return iter(self._messages)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Conversation(messages={len(self._messages)}, session_id={self.session_id})"