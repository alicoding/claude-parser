"""
New API implementation using ResourceManager + Micro-Components.

Maintains identical public interface but uses clean architecture internally.
"""

from pathlib import Path
from typing import List

from .core.resources import get_resource_manager
from .components.file_loader import FileLoader
from .components.token_counter import TokenCounter
from .domain.entities.conversation import Conversation


def load(file_path: str | Path) -> Conversation:
    """
    Load conversation from JSONL file.

    95/5 principle: Same public API, clean architecture internally.
    """
    # Get centralized resources
    resources = get_resource_manager()

    # Use micro-component for loading
    loader = FileLoader(resources)
    raw_data = loader.load(file_path)

    # Convert to domain objects (using existing logic for now)
    # TODO: Replace with micro-component approach
    from .application.conversation_service import ConversationService
    service = ConversationService()
    return service.load_conversation(file_path)


def load_many(file_paths: List[str | Path]) -> List[Conversation]:
    """Load multiple conversations - 95/5 principle."""
    return [load(path) for path in file_paths]


# Token counting using new architecture
def count_tokens(text: str) -> int:
    """Count tokens using micro-component."""
    resources = get_resource_manager()
    counter = TokenCounter(resources)
    return counter.count(text)
