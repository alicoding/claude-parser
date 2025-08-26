"""
Claude Parser - Parse Claude Code JSONL files with ease.

The 95/5 principle: 95% of users just need one line:
    conv = load("session.jsonl")

For the remaining 5%, full power is available through the classes.

Architecture:
- Domain Driven Design (DDD) with clean separation of concerns
- SOLID principles throughout the codebase
- Uses orjson + pydantic per specification for maximum performance
"""

# Import DDD application layer (95/5 factory functions)

# Import analytics tools
from .analytics.analyzer import ConversationAnalytics, TokenCounter
from .application.conversation_service import (
    analyze,
    extract_assistant_messages_between,
    load,
    load_large,
    load_many,
)

# Import discovery tools
from .discovery import find_current_transcript, find_transcript_for_cwd

# Import domain entities
from .domain.entities.conversation import Conversation
from .domain.value_objects.metadata import ConversationMetadata

# Import legacy parser functions (for backward compatibility)
from .infrastructure.jsonl_parser import (
    count_messages,
    parse_jsonl,
    parse_jsonl_streaming,
    validate_claude_format,
    validate_jsonl,
)

# Import models
from .models import (
    AssistantMessage,
    BaseMessage,
    ContentBlock,
    Message,
    MessageType,
    Summary,
    SystemMessage,
    ToolResultContent,
    ToolUseContent,
    UserMessage,
    parse_message,
)

# Export all the important classes and functions
__all__ = [
    # Main API (95% use case) - DDD application layer
    "load",
    "load_large",
    "load_many",
    "analyze",
    "extract_assistant_messages_between",
    # Discovery tools (95% use case)
    "find_current_transcript",
    "find_transcript_for_cwd",
    # Core classes (5% use case) - DDD domain layer
    "Conversation",
    "ConversationMetadata",
    # Message types
    "Message",
    "MessageType",
    "BaseMessage",
    "UserMessage",
    "AssistantMessage",
    "ContentBlock",
    "ToolUseContent",
    "ToolResultContent",
    "Summary",
    "SystemMessage",
    "parse_message",
    # Legacy parser functions (backward compatibility)
    "parse_jsonl",
    "parse_jsonl_streaming",
    "count_messages",
    "validate_jsonl",
    "validate_claude_format",
    # Analytics tools
    "TokenCounter",
    "ConversationAnalytics",
]

__version__ = "0.1.0"
