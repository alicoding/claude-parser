"""
Claude Parser - Parse Claude Code JSONL files with ease.

The 95/5 principle: 95% of users just need one line:
    conv = load("session.jsonl")

For the remaining 5%, full power is available through the classes.

Architecture:
- Domain Driven Design (DDD) with clean separation of concerns
- SOLID principles throughout the codebase
- Uses central JSON service for maximum performance and consistency
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

# Import export tools (new!)
from .export import ProjectConversationExporter

# Import domain entities
from .domain.entities.conversation import Conversation
from .domain.value_objects.metadata import ConversationMetadata

# Import models (structured data objects)
from .models import (
    AssistantMessage,
    ContentBlock,
    Message,
    Summary,
    SystemMessage,
    ToolResultContent,
    ToolUseContent,
    UserMessage,
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
    # Message types (structured data objects)
    "MessageType",
    "Message",
    "UserMessage",
    "AssistantMessage",
    "ContentBlock",
    "ToolUseContent",
    "ToolResultContent",
    "Summary",
    "SystemMessage",
    # Analytics tools
    "TokenCounter",
    "ConversationAnalytics",
    # Export tools (new!)
    "ProjectConversationExporter",
]

__version__ = "0.1.0"
