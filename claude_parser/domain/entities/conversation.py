"""
Conversation entity - Core domain model.

SOLID: Single Responsibility - ONLY conversation representation.
DDD: Entity with identity (session_id).
95/5: Using toolz for all filtering operations.
"""

from typing import Iterator, List, Optional

from toolz import filter as toolz_filter

from ...models import AssistantMessage, Message, Summary, UserMessage
from ...models.content import ToolUseContent, ToolResultContent
from ..filters import ErrorFilter
from ..value_objects.metadata import ConversationMetadata


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
        return list(
            toolz_filter(lambda m: isinstance(m, AssistantMessage), self._messages)
        )

    @property
    def user_messages(self) -> List[UserMessage]:
        """Get user messages using toolz."""
        return list(toolz_filter(lambda m: isinstance(m, UserMessage), self._messages))

    @property
    def tool_uses(self) -> List["ToolUseContent | ToolResultContent"]:
        """Get tool use/result content blocks using toolz."""
        from ...models.content import ToolResultContent, ToolUseContent

        tool_blocks = []
        for msg in self._messages:
            if hasattr(msg, "content_blocks"):
                for block in msg.content_blocks:
                    if isinstance(block, (ToolUseContent, ToolResultContent)):
                        tool_blocks.append(block)
        return tool_blocks

    @property
    def summaries(self) -> List[Summary]:
        """Get summaries using toolz."""
        return list(toolz_filter(lambda m: isinstance(m, Summary), self._messages))

    # Simple query methods
    def filter_messages(self, predicate) -> List[Message]:
        """Filter messages using custom predicate."""
        return list(toolz_filter(predicate, self._messages))

    def search(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """Search messages containing text."""
        if case_sensitive:
            return self.filter_messages(lambda m: query in m.text_content)
        else:
            query_lower = query.lower()
            return self.filter_messages(lambda m: query_lower in m.text_content.lower())

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
            i for i, msg in enumerate(self._messages) if isinstance(msg, Summary)
        ]

        if not summary_indices:
            # No summary, return last 'limit' messages
            return (
                self._messages[-limit:]
                if limit < len(self._messages)
                else self._messages[:]
            )

        # Get messages before last summary
        last_summary_idx = summary_indices[-1]
        start_idx = max(0, last_summary_idx - limit)
        return self._messages[start_idx:last_summary_idx]

    # Alias methods for backward compatibility
    def tool_messages(self) -> List["ToolUseContent | ToolResultContent"]:
        """Alias for tool_uses property for backward compatibility."""
        return self.tool_uses

    def messages_with_errors(self) -> List[Message]:
        """Alias for with_errors() for backward compatibility."""
        return self.with_errors()

    def messages_before_summary(self, limit: int = 10) -> List[Message]:
        """Alias for before_summary() for backward compatibility."""
        return self.before_summary(limit)

    def get_session_boundaries(self) -> List[int]:
        """Get indices where session ID changes.

        Returns:
            List of indices marking session boundaries.
            First message (index 0) is always included as a boundary.
        """
        if not self._messages:
            return []

        boundaries = [0]  # First message is always a boundary
        current_session = getattr(self._messages[0], "session_id", None)

        for i, msg in enumerate(self._messages[1:], 1):
            msg_session = getattr(msg, "session_id", None)
            if msg_session != current_session:
                boundaries.append(i)
                current_session = msg_session

        return boundaries

    # Navigation methods for test compatibility
    def get_by_uuid(self, uuid: str) -> Optional[Message]:
        """Get message by UUID."""
        for msg in self._messages:
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                return msg
        return None

    def filter_by_type(self, message_type: str) -> List[Message]:
        """Filter messages by type string."""
        return [msg for msg in self._messages if msg.type.value == message_type]

    def get_surrounding(
        self, uuid: str, before: int = 2, after: int = 2
    ) -> List[Message]:
        """Get messages surrounding a specific UUID."""
        # Find the message index
        for i, msg in enumerate(self._messages):
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                start_idx = max(0, i - before)
                end_idx = min(len(self._messages), i + after + 1)
                return self._messages[start_idx:end_idx]
        return []

    def get_messages_between_timestamps(
        self, start_timestamp: str, end_timestamp: str
    ) -> List[Message]:
        """Get messages between two timestamps."""
        result = []
        for msg in self._messages:
            if hasattr(msg, "timestamp") and msg.timestamp:
                if start_timestamp <= msg.timestamp <= end_timestamp:
                    result.append(msg)
        return result

    def get_thread_from(self, uuid: str) -> List[Message]:
        """Get thread of messages starting from UUID (simplified implementation)."""
        # Find starting message
        start_idx = None
        for i, msg in enumerate(self._messages):
            if hasattr(msg, "uuid") and msg.uuid == uuid:
                start_idx = i
                break

        if start_idx is None:
            return []

        # Return messages from this point to end of conversation
        # (simplified - a real implementation might track parent/child relationships)
        return self._messages[start_idx:]

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
