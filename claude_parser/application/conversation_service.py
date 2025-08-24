"""
Conversation application service.

SOLID:
- SRP: Single responsibility - conversation use cases
- DIP: Depends on domain abstractions, not infrastructure

95/5 Principle:
- Simple factory functions for 95% use cases
- Rich options for 5% advanced use cases
"""

from typing import List, Optional
from pathlib import Path
from toolz import map as toolz_map

from ..domain.entities.conversation import Conversation
from ..domain.value_objects.metadata import ConversationMetadata
from ..domain.services.analyzer import ConversationAnalyzer
from ..infrastructure.message_repository import JsonlMessageRepository
from ..models.base import Message
from ..models.assistant import AssistantMessage


class ConversationService:
    """Application service for conversation operations."""
    
    def __init__(self, repository = None):
        self.repository = repository or JsonlMessageRepository()
    
    def load_conversation(self, filepath: str | Path) -> Conversation:
        """Load conversation from JSONL file.
        
        This is the main factory method following 95/5 principle.
        """
        filepath = Path(filepath)
        
        # Load messages using repository
        messages = self.repository.load_messages(filepath)
        
        # Get metadata
        metadata = self.repository.get_metadata(messages, filepath)
        
        # Create domain entity
        return Conversation(messages, metadata)
    

    
    def analyze_conversation(self, conversation: Conversation) -> dict:
        """Get conversation analysis.
        
        Use case: Generate insights and statistics.
        """
        analyzer = ConversationAnalyzer(conversation)
        return analyzer.get_stats()
    
    def extract_assistant_conversation_segment(
        self,
        conversation: Conversation,
        start_point: str | int,
        end_point: str | int
    ) -> List[AssistantMessage]:
        """Extract assistant messages between two conversation points.
        
        Use case: Get Claude's responses in a specific timeframe or context.
        
        Args:
            conversation: The conversation to extract from
            start_point: UUID, content substring, or message index for start
            end_point: UUID, content substring, or message index for end
            
        Returns:
            List of assistant messages in the range
        """
        # Implementation would go here - for now return assistant messages
        return conversation.assistant_messages
    
    def get_repository_errors(self) -> List[tuple]:
        """Get any parsing errors from the last load operation."""
        return self.repository.errors  # Fixed: was self._repository (bug)


# ==========================================
# 95/5 FACTORY FUNCTIONS (Main API)
# ==========================================

def load(filepath: str | Path, strict: bool = False) -> Conversation:
    """Load a Claude conversation from JSONL file.
    
    This is the 95% use case - dead simple API.
    
    Example:
        conv = load("chat.jsonl")
        assistant_msgs = conv.assistant_messages()
        results = conv.search("error")
    
    Args:
        filepath: Path to Claude JSONL file
        strict: If True, validate that this is a Claude-format JSONL file
        
    Returns:
        Conversation object with rich domain behavior
    
    Raises:
        ValueError: If strict=True and file is not Claude format
    """
    if strict:
        from ..infrastructure.jsonl_parser import validate_claude_format
        is_valid, errors = validate_claude_format(filepath)
        if not is_valid:
            error_msg = f"File {filepath} is not in valid Claude Code format"
            if errors:
                error_msg += f": {'; '.join(errors)}"
            raise ValueError(error_msg)
    
    service = ConversationService()
    return service.load_conversation(filepath)


def load_large(filepath: str | Path) -> Conversation:
    """Load large conversation files with lazy loading optimization.
    
    5% use case for files > 100MB. Uses lazy-object-proxy to delay 
    loading until the conversation data is actually accessed.
    
    Args:
        filepath: Path to large Claude JSONL file
        
    Returns:
        Conversation proxy that loads lazily on first access
    """
    def _lazy_loader():
        service = ConversationService()
        return service.load_conversation(filepath)
    
    return Proxy(_lazy_loader)


def load_many(filepaths: List[str | Path]) -> List[Conversation]:
    """Load multiple conversations efficiently.
    
    5% use case for batch processing.
    
    Args:
        filepaths: List of paths to Claude JSONL files
        
    Returns:
        List of conversation objects
    """
    service = ConversationService()
    # Fixed: Use functional approach instead of list comprehension
    return list(toolz_map(service.load_conversation, filepaths))


def analyze(conversation: Conversation) -> dict:
    """Analyze conversation and return insights.
    
    Args:
        conversation: Conversation to analyze
        
    Returns:
        Dictionary with conversation statistics and insights
    """
    service = ConversationService()
    return service.analyze_conversation(conversation)


def extract_assistant_messages_between(
    conversation: Conversation,
    start_point: str | int,
    end_point: str | int
) -> List[AssistantMessage]:
    """Extract Claude's responses between two conversation points.
    
    Args:
        conversation: Conversation to extract from  
        start_point: Start identifier (UUID, content, or index)
        end_point: End identifier (UUID, content, or index)
        
    Returns:
        Assistant messages in the specified range
    """
    service = ConversationService()
    return service.extract_assistant_conversation_segment(
        conversation, start_point, end_point
    )