"""
Conversation entity - Core domain model.

SOLID: Single Responsibility - ONLY conversation representation.
DDD: Entity with identity (session_id).
95/5: Using toolz for all filtering operations.
"""

from typing import Iterator, List, Optional


from ...models import AssistantMessage, Message, Summary, UserMessage
from ...models.content import ToolUseContent, ToolResultContent
from ..value_objects.metadata import ConversationMetadata
from ..delegates import MessageFilter, MessageNavigator, SessionAnalyzer


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
        # Initialize delegates
        self._filter = MessageFilter(messages)
        self._navigator = MessageNavigator(messages)
        self._session_analyzer = SessionAnalyzer(messages)
        # Initialize delegates
        self._filter = MessageFilter(messages)
        self._navigator = MessageNavigator(messages)
        self._session_analyzer = SessionAnalyzer(messages)

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
        """Get assistant messages using delegate."""
        return self._filter.assistant_messages()

    @property
    def user_messages(self) -> List[UserMessage]:
        """Get user messages using delegate."""
        return self._filter.user_messages()

    @property
    def tool_uses(self) -> List["ToolUseContent | ToolResultContent"]:
        """Get tool use/result content blocks using delegate."""
        return self._filter.tool_blocks()

    @property
    def summaries(self) -> List[Summary]:
        """Get summaries using delegate."""
        return self._filter.summaries()

    # Simple query methods
    def filter_messages(self, predicate) -> List[Message]:
        """Filter messages using custom predicate."""
        return self._filter.by_predicate(predicate)

    def search(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """Search messages containing text."""
        return self._filter.containing_text(query, case_sensitive)

    def filter(self, predicate) -> List[Message]:
        """Alias for filter_messages for backward compatibility."""
        return self.filter_messages(predicate)

    def with_errors(self) -> List[Message]:
        """Find messages with errors."""
        return self._filter.with_errors()

    def before_summary(self, limit: int = 10) -> List[Message]:
        """Get messages before the last summary."""
        return self._navigator.before_summary(limit)

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
        return self._session_analyzer.get_boundaries()

    # Navigation methods for test compatibility
    def get_by_uuid(self, uuid: str) -> Optional[Message]:
        """Get message by UUID."""
        return self._navigator.get_by_uuid(uuid)

    def filter_by_type(self, message_type: str) -> List[Message]:
        """Filter messages by type string."""
        return self._filter.by_type_string(message_type)

    def get_surrounding(
        self, uuid: str, before: int = 2, after: int = 2
    ) -> List[Message]:
        """Get messages surrounding a specific UUID."""
        return self._navigator.get_surrounding(uuid, before, after)

    def get_messages_between_timestamps(
        self, start_timestamp: str, end_timestamp: str
    ) -> List[Message]:
        """Get messages between two timestamps."""
        return self._navigator.between_timestamps(start_timestamp, end_timestamp)

    def get_messages_between_uuids(self, start_uuid: str, end_uuid: str) -> List[AssistantMessage]:
        """Get assistant messages between two UUIDs."""
        # Find start and end indices
        start_idx = end_idx = -1
        for i, msg in enumerate(self._messages):
            if msg.uuid == start_uuid:
                start_idx = i
            elif msg.uuid == end_uuid:
                end_idx = i
                break

        if start_idx == -1 or end_idx == -1:
            return []

        # Get messages between the UUIDs and filter for assistant messages
        messages_between = self._messages[start_idx + 1:end_idx]
        return [msg for msg in messages_between if isinstance(msg, AssistantMessage)]

    def get_thread_from(self, uuid: str) -> List[Message]:
        """Get thread of messages starting from UUID (simplified implementation)."""
        return self._navigator.get_thread_from(uuid)

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
