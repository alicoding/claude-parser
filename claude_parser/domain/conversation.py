"""
Conversation domain entity - Core business logic using functional programming.

SOLID Principles:
- SRP: Single responsibility - represent a conversation
- OCP: Open for extension via composition
- LSP: Can be substituted for base conversation interface
- ISP: Focused interface, no god methods
- DIP: Depends on abstractions, not concretions

DDD Principles:
- Entity: Has identity (session_id, filepath)
- Aggregate Root: Controls access to messages
- Rich Domain Model: Contains business behavior

95/5 Principle:
- NO manual loops, use toolz/more-itertools
- NO list comprehensions, use functional operations
- NO mutable state, use immutable operations
"""

from typing import List, Optional, Iterator, Protocol
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
import pendulum
from toolz import (
    filter as toolz_filter,
    map as toolz_map,
    pipe,
    concat,
    take,
    drop,
    first
)
from more_itertools import one, locate

from ..models import Message, AssistantMessage, UserMessage, ToolUse, ToolResult, Summary


class MessageFilter(Protocol):
    """Strategy pattern for message filtering."""
    
    def matches(self, message: Message) -> bool:
        """Check if message matches filter criteria."""
        ...


class MessageRepository(ABC):
    """Repository pattern for message data access."""
    
    @abstractmethod
    def load_messages(self, filepath: Path) -> List[Message]:
        """Load messages from data source."""
        ...


@dataclass(frozen=True)
class ConversationMetadata:
    """Value object for conversation metadata."""
    session_id: Optional[str]
    filepath: Path
    current_dir: Optional[str]
    git_branch: Optional[str]
    message_count: int
    error_count: int


class Conversation:
    """
    Conversation aggregate root using functional programming.
    
    Represents a complete Claude conversation with rich domain behavior.
    Following 95/5 principle: Simple to use, powerful when needed.
    
    Example 95% usage:
        conv = load("file.jsonl")  # Simple factory function
        assistant_msgs = conv.assistant_messages
        results = conv.search("error")
    """
    
    def __init__(
        self, 
        messages: List[Message], 
        metadata: ConversationMetadata
    ):
        """Initialize conversation with messages and metadata.
        
        Note: Use factory functions (load, from_jsonl) instead of direct construction.
        """
        self._messages = messages
        self._metadata = metadata
        
        # Build indices for O(1) operations functionally
        self._uuid_index = dict(pipe(
            messages,
            lambda msgs: toolz_filter(lambda msg: hasattr(msg, 'uuid'), msgs),
            lambda msgs: toolz_map(lambda msg: (msg.uuid, msg), msgs)
        ))
        
        self._uuid_to_index = dict(pipe(
            enumerate(messages),
            lambda items: toolz_filter(lambda x: hasattr(x[1], 'uuid'), items),
            lambda items: toolz_map(lambda x: (x[1].uuid, x[0]), items)
        ))
        
        # Build timestamp index functionally
        self._timestamps = list(pipe(
            messages,
            lambda msgs: toolz_filter(lambda msg: hasattr(msg, 'timestamp'), msgs),
            lambda msgs: toolz_map(lambda msg: msg.timestamp, msgs)
        ))
        
        self._timestamp_indices = list(range(len(messages)))
    
    # ==========================================
    # CORE PROPERTIES (95% use cases)
    # ==========================================
    
    @property
    def metadata(self) -> ConversationMetadata:
        """Get conversation metadata."""
        return self._metadata
    
    @property
    def session_id(self) -> Optional[str]:
        """Get session ID."""
        return self._metadata.session_id
    
    @property
    def messages(self) -> List[Message]:
        """Get all messages (immutable view)."""
        return self._messages.copy()
    
    @property
    def assistant_messages(self) -> List[AssistantMessage]:
        """Get only assistant messages."""
        return list(toolz_filter(lambda m: isinstance(m, AssistantMessage), self._messages))
    
    @property
    def user_messages(self) -> List[UserMessage]:
        """Get only user messages."""
        return list(toolz_filter(lambda m: isinstance(m, UserMessage), self._messages))
    
    @property
    def tool_uses(self) -> List[ToolUse | ToolResult]:
        """Get all tool use and tool result messages."""
        return list(toolz_filter(lambda m: isinstance(m, (ToolUse, ToolResult)), self._messages))
    
    @property
    def summaries(self) -> List[Summary]:
        """Get all summary messages."""
        return list(toolz_filter(lambda m: isinstance(m, Summary), self._messages))
    
    @property
    def current_dir(self) -> Optional[str]:
        """Get current working directory from metadata."""
        return self._metadata.current_dir
    
    @property
    def git_branch(self) -> Optional[str]:
        """Get git branch from metadata."""
        return self._metadata.git_branch
    
    @property
    def filepath(self) -> Path:
        """Get filepath from metadata."""
        return self._metadata.filepath
    
    def tool_messages(self) -> List[ToolUse | ToolResult]:
        """Get all tool-related messages."""
        return list(toolz_filter(lambda m: isinstance(m, (ToolUse, ToolResult)), self._messages))
    
    # Backward compatibility - provide method versions that return properties
    def get_assistant_messages(self) -> List[AssistantMessage]:
        """Method version of assistant_messages property for backward compatibility."""
        return self.assistant_messages
    
    def get_user_messages(self) -> List[UserMessage]:
        """Method version of user_messages property for backward compatibility."""  
        return self.user_messages
    
    def get_summaries(self) -> List[Summary]:
        """Method version of summaries property for backward compatibility."""
        return self.summaries
    
    # ==========================================
    # DOMAIN OPERATIONS (Business Logic)
    # ==========================================
    
    def search(self, query: str, case_sensitive: bool = False) -> List[Message]:
        """Search messages by text content.
        
        Domain operation: Text-based message retrieval.
        """
        if not case_sensitive:
            query = query.lower()
        
        def matches_query(message: Message) -> bool:
            content = message.text_content
            if not case_sensitive:
                content = content.lower()
            return query in content
        
        return self.filter_messages(matches_query)
    
    def messages_with_errors(self) -> List[Message]:
        """Find messages containing error indicators.
        
        Domain operation: Error detection and analysis.
        """
        error_keywords = ['error', 'exception', 'failed', 'failure', 'traceback']
        
        def has_error_keywords(message: Message) -> bool:
            content = message.text_content.lower()
            # Replace generator expression with functional approach
            return pipe(
                error_keywords,
                lambda keywords: toolz_map(lambda keyword: keyword in content, keywords),
                any
            )
        
        return self.filter_messages(has_error_keywords)
    
    def with_errors(self) -> List[Message]:
        """Alias for messages_with_errors() for backwards compatibility."""
        return self.messages_with_errors()
    
    def filter(self, predicate) -> List[Message]:
        """Alias for filter_messages() for backwards compatibility."""
        return self.filter_messages(predicate)
    
    def before_summary(self, limit: int = 20) -> List[Message]:
        """Alias for messages_before_summary() for backwards compatibility."""
        return self.messages_before_summary(limit)
    
    def messages_before_summary(self, limit: int = 20) -> List[Message]:
        """Get messages before the last summary.
        
        Domain operation: Context extraction for analysis.
        """
        # Find last summary index functionally
        summary_indices = list(locate(
            self._messages,
            lambda msg: isinstance(msg, Summary)
        ))
        
        if not summary_indices:
            # No summary found, return last N messages
            start_idx = max(0, len(self._messages) - limit)
            return self._messages[start_idx:]
        
        # Get last summary index
        last_summary_idx = summary_indices[-1]
        
        # Get messages before summary
        start_idx = max(0, last_summary_idx - limit)
        return self._messages[start_idx:last_summary_idx]
    
    def filter_messages(self, predicate) -> List[Message]:
        """Filter messages using custom predicate.
        
        5% use case: Maximum flexibility for complex queries.
        """
        return list(toolz_filter(predicate, self._messages))
    
    def extract_assistant_messages_between(
        self, 
        start_identifier: str | int, 
        end_identifier: str | int
    ) -> List[AssistantMessage]:
        """Extract assistant messages between two points.
        
        Args:
            start_identifier: UUID, content substring, or message index
            end_identifier: UUID, content substring, or message index
            
        Returns:
            Assistant messages in the specified range
        """
        start_idx = self._find_message_index(start_identifier)
        end_idx = self._find_message_index(end_identifier, start_from=start_idx + 1)
        
        if start_idx == -1 or end_idx == -1:
            return []
        
        # Extract range and filter for assistant messages functionally
        range_messages = self._messages[start_idx:end_idx + 1]
        return list(toolz_filter(lambda m: isinstance(m, AssistantMessage), range_messages))
    
    def _find_message_index(self, identifier: str | int, start_from: int = 0) -> int:
        """Find message index by various identifiers functionally."""
        if isinstance(identifier, int):
            return identifier if 0 <= identifier < len(self._messages) else -1
        
        # Search by UUID or content functionally
        def matches_identifier(indexed_msg: tuple) -> bool:
            idx, message = indexed_msg
            if idx < start_from:
                return False
            
            # Check UUID
            if hasattr(message, 'uuid') and message.uuid == identifier:
                return True
            
            # Check content substring
            if identifier.lower() in message.text_content.lower():
                return True
            
            return False
        
        # Find first matching message
        matching_indices = list(locate(
            enumerate(self._messages),
            matches_identifier
        ))
        
        return matching_indices[0] if matching_indices else -1
    
    # ==========================================
    # NAVIGATION METHODS (Navigation Domain)
    # ==========================================
    
    def get_by_uuid(self, uuid: str) -> Optional[Message]:
        """Get message by UUID with O(1) lookup.
        
        95/5: Fast UUID lookup via hashmap.
        """
        return self._uuid_index.get(uuid)
    
    def get_surrounding(self, uuid: str, before: int = 2, after: int = 2) -> List[Message]:
        """Get messages surrounding a specific message.
        
        Args:
            uuid: UUID of the target message
            before: Number of messages before target
            after: Number of messages after target
            
        Returns:
            List of messages around target (up to before + 1 + after messages)
        """
        # Use our O(1) index instead of looping
        target_idx = self._uuid_to_index.get(uuid, -1)
        
        if target_idx == -1:
            return []
        
        # Simple slicing - this is the Pythonic way
        start_idx = max(0, target_idx - before)
        end_idx = min(len(self._messages), target_idx + after + 1)
        
        return self._messages[start_idx:end_idx]
    
    def get_messages_between_timestamps(self, start: Optional[str], end: Optional[str]) -> List[Message]:
        """Get messages between two timestamps functionally.
        
        Args:
            start: Start timestamp (ISO format or pendulum instance) 
            end: End timestamp (ISO format or pendulum instance)
            
        Returns:
            Messages within the time range
        """
        # Handle None timestamps
        if not start or not end:
            return []
            
        # Use pendulum for robust timestamp handling
        if isinstance(start, str):
            start_dt = pendulum.parse(start)
        else:
            start_dt = start
            
        if isinstance(end, str):
            end_dt = pendulum.parse(end)
        else:
            end_dt = end
        
        # Filter messages functionally
        def is_in_range(msg: Message) -> bool:
            if not hasattr(msg, 'timestamp') or not msg.timestamp:
                return False
            msg_dt = pendulum.parse(msg.timestamp) if isinstance(msg.timestamp, str) else msg.timestamp
            return start_dt <= msg_dt <= end_dt
        
        return list(toolz_filter(is_in_range, self._messages))
    
    def get_thread_from(self, uuid: str) -> List[Message]:
        """Get all messages in a thread starting from a specific message.
        
        Follows parentUuid chain forward to find replies.
        Uses NetworkX as recommended by research for graph operations.
        
        Args:
            uuid: Starting message UUID
            
        Returns:
            Thread of messages from this point forward
        """
        import networkx as nx
        
        # Build conversation graph (research: NetworkX is 95/5 solution for trees)
        G = nx.DiGraph()
        
        # Add all messages as nodes with their data functionally
        valid_messages = list(toolz_filter(
            lambda msg: hasattr(msg, 'uuid') and msg.uuid,
            self._messages
        ))
        
        # Add nodes
        pipe(
            valid_messages,
            lambda msgs: toolz_map(lambda msg: G.add_node(msg.uuid, data=msg), msgs),
            list
        )
        
        # Add parent-child edges functionally
        pipe(
            valid_messages,
            lambda msgs: toolz_filter(lambda msg: hasattr(msg, 'parent_uuid') and msg.parent_uuid and msg.parent_uuid in G, msgs),
            lambda msgs: toolz_map(lambda msg: G.add_edge(msg.parent_uuid, msg.uuid), msgs),
            list
        )
        
        # Get thread using NetworkX
        if uuid not in G:
            return []
        
        # Build thread: starting message + descendants
        thread_uuids = [uuid] + list(nx.descendants(G, uuid))
        return list(pipe(
            thread_uuids,
            lambda uuids: toolz_map(lambda u: G.nodes[u]['data'], uuids),
            list
        ))
    
    def filter_by_type(self, message_type: str) -> List[Message]:
        """Filter messages by type string functionally.
        
        Args:
            message_type: Type string ('user', 'assistant', 'tool_use', etc.)
            
        Returns:
            Messages matching the specified type
        """
        return list(toolz_filter(
            lambda msg: hasattr(msg, 'type') and msg.type.value == message_type,
            self._messages
        ))
    
    # ==========================================
    # EXPORT METHODS
    # ==========================================
    
    def export_for_mem0(
        self,
        include_tools: bool = False,
        include_meta: bool = False,
        include_summaries: bool = False
    ) -> dict:
        """Export conversation in mem0-compatible format.
        
        Filters conversation messages for memory system ingestion.
        By default, excludes tool uses, meta messages, and summaries
        to focus on actual conversation content.
        
        Args:
            include_tools: Include tool use and result messages
            include_meta: Include meta/system messages  
            include_summaries: Include summary messages
            
        Returns:
            Dict with 'messages' and 'metadata' for mem0 ingestion
            
        Example:
            >>> conv = load("conversation.jsonl")
            >>> data = conv.export_for_mem0()  # Only user/assistant msgs
            >>> data = conv.export_for_mem0(include_tools=True)  # With tools
        """
        from toolz import pipe, filter as toolz_filter, map as toolz_map
        
        # Define filter predicate based on options
        def should_include(msg: Message) -> bool:
            # Always include user and assistant messages
            if isinstance(msg, (UserMessage, AssistantMessage)):
                return True
            
            # Conditionally include other types
            if isinstance(msg, (ToolUse, ToolResult)) and include_tools:
                return True
            
            if isinstance(msg, Summary) and include_summaries:
                return True
            
            # Check for meta messages (if they have a meta attribute)
            if hasattr(msg, 'meta') and msg.meta and include_meta:
                return True
            
            return False
        
        # Filter messages functionally
        filtered_messages = list(pipe(
            self._messages,
            lambda msgs: toolz_filter(should_include, msgs),
            list
        ))
        
        # Convert to mem0 format functionally
        def message_to_mem0(msg: Message) -> dict:
            base_msg = {
                "role": "user" if isinstance(msg, UserMessage) else "assistant",
                "content": msg.text_content,
                "timestamp": msg.timestamp
            }
            
            # Add type info for non-conversation messages
            if isinstance(msg, ToolUse):
                base_msg["type"] = "tool_use"
                base_msg["tool_name"] = msg.name
                base_msg["tool_input"] = msg.parameters
            elif isinstance(msg, ToolResult):
                base_msg["type"] = "tool_result"
                base_msg["output"] = msg.tool_use_result
            elif isinstance(msg, Summary):
                base_msg["type"] = "summary"
                
            return base_msg
        
        mem0_messages = list(pipe(
            filtered_messages,
            lambda msgs: toolz_map(message_to_mem0, msgs),
            list
        ))
        
        # Build metadata
        metadata = {
            "session_id": self.session_id,
            "message_count": len(mem0_messages),
            "original_count": len(self._messages),
            "filtered_count": len(self._messages) - len(mem0_messages),
            "has_errors": self._metadata.error_count > 0,
            "current_dir": self.current_dir,
            "git_branch": self.git_branch
        }
        
        return {
            "messages": mem0_messages,
            "metadata": metadata
        }
    
    # ==========================================
    # COLLECTION INTERFACE
    # ==========================================
    
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
        return (
            f"Conversation("
            f"messages={len(self._messages)}, "
            f"session_id={self.session_id})"
        )


# ==========================================
# DOMAIN SERVICES
# ==========================================

class ConversationAnalyzer:
    """Domain service for conversation analysis."""
    
    def __init__(self, conversation):
        """Initialize analyzer with a conversation."""
        self.conversation = conversation
    
    def get_stats(self) -> dict:
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


# ==========================================
# MESSAGE FILTERS (Strategy Pattern)
# ==========================================

class ContentFilter:
    """Filter messages by content."""
    
    def __init__(self, query: str, case_sensitive: bool = False):
        self.query = query.lower() if not case_sensitive else query
        self.case_sensitive = case_sensitive
    
    def matches(self, message: Message) -> bool:
        content = message.text_content
        if not self.case_sensitive:
            content = content.lower()
        return self.query in content


class TypeFilter:
    """Filter messages by type."""
    
    def __init__(self, message_type: type):
        self.message_type = message_type
    
    def matches(self, message: Message) -> bool:
        return isinstance(message, self.message_type)


class ErrorFilter:
    """Filter messages containing errors."""
    
    ERROR_KEYWORDS = ['error', 'exception', 'failed', 'failure', 'traceback']
    
    def matches(self, message: Message) -> bool:
        content = message.text_content.lower()
        # Replace generator expression with functional approach
        return pipe(
            self.ERROR_KEYWORDS,
            lambda keywords: toolz_map(lambda keyword: keyword in content, keywords),
            any
        )