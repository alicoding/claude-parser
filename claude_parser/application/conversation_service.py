"""
Conversation application service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from pathlib import Path
from typing import List, Union
from ..core.resources import get_resource_manager
from ..components.file_loader import FileLoader
from ..domain.entities.conversation import Conversation


class ConversationService:
    """Clean conversation service using ResourceManager pattern."""

    def __init__(self):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        self.loader = FileLoader(self.resources)

    def load_conversation(self, filepath: str | Path) -> Conversation:
        """Load conversation using clean architecture."""
        # Use micro-component for file loading
        raw_data = self.loader.load(filepath)

        # Use existing repository temporarily (TODO: replace with micro-components)
        from ..infrastructure.message_repository import JsonlMessageRepository
        repo = JsonlMessageRepository()
        messages = repo.load_messages(filepath)
        metadata = repo.get_metadata(messages, filepath)

        # Create conversation entity
        return Conversation(messages, metadata)


# 95/5 Factory Functions (Public API)
def load(filepath: str | Path) -> Conversation:
    """Load single conversation - 95% use case."""
    service = ConversationService()
    return service.load_conversation(filepath)


def load_many(filepaths: List[str | Path]) -> List[Conversation]:
    """Load multiple conversations - 95% use case."""
    return [load(path) for path in filepaths]


def analyze(filepath: str | Path):
    """Analyze conversation - 95% use case."""
    conv = load(filepath)
    # TODO: Replace with micro-component analytics
    return {"messages": len(conv.messages)}


def load_large(filepath: str | Path) -> Conversation:
    """Load large conversation - same as load for now."""
    return load(filepath)


def extract_assistant_messages_between(filepath: str | Path, start_uuid: str, end_uuid: str):
    """Extract messages between UUIDs - 5% use case."""
    conv = load(filepath)
    return conv.get_messages_between_uuids(start_uuid, end_uuid)
