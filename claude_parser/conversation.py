"""
Conversation class - the main interface for Claude JSONL files.
"""

from typing import List, Optional, Iterator, Any
from pathlib import Path
from loguru import logger

from .parser import parse_jsonl, parse_jsonl_streaming
from .models import (
    Message, MessageType, BaseMessage,
    UserMessage, AssistantMessage, ToolUse, ToolResult, 
    Summary, SystemMessage, parse_message
)


class Conversation:
    """Represents a Claude conversation from JSONL file.
    
    This is the main interface for working with Claude Code exports.
    Follows the 95/5 principle - simple by default, powerful when needed.
    """
    
    def __init__(self, filepath: str | Path):
        """Initialize conversation from JSONL file.
        
        Args:
            filepath: Path to Claude JSONL file
        """
        self.filepath = Path(filepath)
        self._raw_messages: List[dict] = []
        self._messages: List[Message] = []
        self._session_id: Optional[str] = None
        self._errors: List[tuple[int, str]] = []
        
        # Load and parse messages
        self._load()
    
    def _load(self) -> None:
        """Load and parse messages from JSONL file."""
        try:
            # Parse JSONL file
            self._raw_messages = parse_jsonl(self.filepath)
            
            # Convert to typed messages
            for idx, raw_msg in enumerate(self._raw_messages):
                msg = parse_message(raw_msg)
                if msg:
                    self._messages.append(msg)
                    
                    # Extract session ID from first message that has one
                    if not self._session_id and hasattr(msg, 'session_id') and msg.session_id:
                        self._session_id = msg.session_id
                else:
                    self._errors.append((idx, "Failed to parse message"))
            
            logger.info(f"Loaded {len(self._messages)} messages from {self.filepath.name}")
            if self._errors:
                logger.warning(f"Failed to parse {len(self._errors)} messages")
                
        except Exception as e:
            logger.error(f"Failed to load conversation: {e}")
            raise
    
    @property
    def messages(self) -> List[Message]:
        """Get all messages in the conversation."""
        return self._messages
    
    @property
    def session_id(self) -> Optional[str]:
        """Get session ID if available."""
        return self._session_id
    
    @property
    def assistant_messages(self) -> List[AssistantMessage]:
        """Get only assistant messages."""
        return [m for m in self._messages if isinstance(m, AssistantMessage)]
    
    @property
    def user_messages(self) -> List[UserMessage]:
        """Get only user messages."""
        return [m for m in self._messages if isinstance(m, UserMessage)]
    
    @property
    def tools(self) -> List[ToolUse | ToolResult]:
        """Get all tool use and result messages (alias for tool_uses)."""
        return self.tool_uses
    
    @property
    def tool_uses(self) -> List[ToolUse | ToolResult]:
        """Get all tool use and result messages.
        
        This includes both standalone tool messages AND tool uses/results
        embedded within assistant/user message content.
        """
        tools = []
        
        # Get standalone tool messages
        for msg in self._messages:
            if isinstance(msg, (ToolUse, ToolResult)):
                tools.append(msg)
        
        # Extract embedded tools from message content
        tools.extend(self._extract_embedded_tools())
        
        return tools
    
    def _extract_embedded_tools(self) -> List[ToolUse | ToolResult]:
        """Extract tool uses/results embedded in message content."""
        from .models import parse_message
        
        embedded_tools = []
        
        for msg in self._messages:
            # Check if message has structured content
            message_dict = getattr(msg, 'message', None)
            if not message_dict:
                continue
            
            content = message_dict.get('content', [])
            if not isinstance(content, list):
                continue
            
            # Look for tool_use and tool_result items in content
            for item in content:
                if not isinstance(item, dict):
                    continue
                
                item_type = item.get('type', '')
                
                if item_type == 'tool_use':
                    # Create ToolUse from embedded content
                    tool_data = {
                        'type': 'tool_use',
                        'toolUseID': item.get('id'),  # Use correct alias
                        'name': item.get('name'),
                        'parameters': item.get('input', {}),  # Claude uses 'input' not 'parameters'
                        'sessionId': getattr(msg, 'session_id', None),
                        'timestamp': getattr(msg, 'timestamp', None),
                        'uuid': getattr(msg, 'uuid', None),
                        'parentUuid': getattr(msg, 'parent_uuid', None),
                    }
                    
                    tool_msg = parse_message(tool_data)
                    if tool_msg:
                        embedded_tools.append(tool_msg)
                
                elif item_type == 'tool_result':
                    # Create ToolResult from embedded content
                    result_data = {
                        'type': 'tool_result',
                        'toolUseID': item.get('tool_use_id'),
                        'toolUseResult': item.get('content', ''),
                        'sessionId': getattr(msg, 'session_id', None),
                        'timestamp': getattr(msg, 'timestamp', None),
                        'uuid': getattr(msg, 'uuid', None),
                        'parentUuid': getattr(msg, 'parent_uuid', None),
                    }
                    
                    result_msg = parse_message(result_data)
                    if result_msg:
                        embedded_tools.append(result_msg)
        
        return embedded_tools
    
    @property
    def summaries(self) -> List[Summary]:
        """Get all summary messages."""
        return [m for m in self._messages if isinstance(m, Summary)]
    
    @property
    def errors(self) -> List[tuple[int, str]]:
        """Get parsing errors if any."""
        return self._errors
    
    @property
    def current_dir(self) -> Optional[str]:
        """Get current working directory from messages."""
        for msg in self._messages:
            if hasattr(msg, '__dict__'):
                raw = msg.__dict__
                if 'cwd' in raw:
                    return raw['cwd']
        # Check raw messages for cwd field
        for raw in self._raw_messages:
            if 'cwd' in raw:
                return raw['cwd']
        return None
    
    @property
    def git_branch(self) -> Optional[str]:
        """Get git branch from messages."""
        for raw in self._raw_messages:
            if 'gitBranch' in raw:
                return raw['gitBranch']
        return None
    
    def filter(self, predicate) -> List[Message]:
        """Filter messages by a predicate function.
        
        Args:
            predicate: Function that takes a message and returns bool
            
        Returns:
            List of messages that match the predicate
        """
        return [m for m in self._messages if predicate(m)]
    
    def search(self, text: str, case_sensitive: bool = False) -> List[Message]:
        """Search for messages containing text.
        
        Args:
            text: Text to search for
            case_sensitive: Whether search is case sensitive
            
        Returns:
            Messages containing the text
        """
        if not case_sensitive:
            text = text.lower()
        
        results = []
        for msg in self._messages:
            # All message types have text_content property
            content = msg.text_content
            
            if not case_sensitive:
                content = content.lower()
            
            if text in content:
                results.append(msg)
        
        return results
    
    def before_summary(self, limit: int = 20) -> List[Message]:
        """Get messages before the last summary.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of messages before the summary
        """
        # Find last summary
        summary_idx = -1
        for i in range(len(self._messages) - 1, -1, -1):
            if isinstance(self._messages[i], Summary):
                summary_idx = i
                break
        
        if summary_idx == -1:
            # No summary found, return last N messages
            return self._messages[-limit:] if len(self._messages) > limit else self._messages
        
        # Get messages before summary
        start_idx = max(0, summary_idx - limit)
        return self._messages[start_idx:summary_idx]
    
    def with_errors(self) -> List[Message]:
        """Get messages that contain error indicators.
        
        Returns:
            Messages that likely contain errors
        """
        error_keywords = ['error', 'exception', 'failed', 'failure', 'traceback']
        results = []
        
        for msg in self._messages:
            # All message types have text_content property
            content = msg.text_content.lower()
            
            if any(keyword in content for keyword in error_keywords):
                results.append(msg)
        
        return results
    
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
        return f"Conversation(messages={len(self._messages)}, session_id={self._session_id})"
    
    def get_surrounding(self, uuid: str, before: int = 5, after: int = 5) -> List[Message]:
        """Get messages surrounding a specific message.
        
        Args:
            uuid: UUID of the target message
            before: Number of messages before target
            after: Number of messages after target
            
        Returns:
            List of messages around the target
        """
        # Find index of target message
        target_idx = None
        for i, msg in enumerate(self._messages):
            if msg.uuid == uuid:
                target_idx = i
                break
        
        if target_idx is None:
            return []
        
        # Get surrounding messages
        start = max(0, target_idx - before)
        end = min(len(self._messages), target_idx + after + 1)
        
        return self._messages[start:end]
    
    def get_messages_between_timestamps(self, start: str, end: str) -> List[Message]:
        """Get messages between two timestamps.
        
        Args:
            start: Start timestamp (ISO format)
            end: End timestamp (ISO format)
            
        Returns:
            Messages within the time range
        """
        results = []
        for msg in self._messages:
            if msg.timestamp and start <= msg.timestamp <= end:
                results.append(msg)
        return results
    
    def get_thread_from(self, uuid: str) -> List[Message]:
        """Get thread of messages starting from given UUID.
        
        Args:
            uuid: UUID to start thread from
            
        Returns:
            List of messages in the thread
        """
        thread = []
        current_uuid = uuid
        
        # Build UUID to message map for fast lookup
        uuid_map = {msg.uuid: msg for msg in self._messages if msg.uuid}
        
        while current_uuid and current_uuid in uuid_map:
            msg = uuid_map[current_uuid]
            thread.append(msg)
            
            # Find next message that references this one as parent
            next_uuid = None
            for m in self._messages:
                if hasattr(m, 'parent_uuid') and m.parent_uuid == current_uuid:
                    next_uuid = m.uuid
                    break
            current_uuid = next_uuid
        
        return thread
    
    def get_by_uuid(self, uuid: str) -> Optional[Message]:
        """Get message by UUID.
        
        Args:
            uuid: UUID to find
            
        Returns:
            Message with the UUID or None
        """
        for msg in self._messages:
            if msg.uuid == uuid:
                return msg
        return None
    
    def filter_by_type(self, msg_type: str) -> List[Message]:
        """Filter messages by type.
        
        Args:
            msg_type: Message type to filter by
            
        Returns:
            Messages of the specified type
        """
        return [m for m in self._messages if m.type.value == msg_type]