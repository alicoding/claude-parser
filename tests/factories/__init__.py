"""Test factories for eliminating test boilerplate and duplication.

This module provides factory_boy factories that follow the 95/5 principle:
- 95%: Framework handles data generation, setup/teardown
- 5%: Custom test logic
"""

from .conversation import ConversationEventFactory, UserMessageFactory, AssistantMessageFactory
from .project import ProjectFactory, TranscriptFactory

__all__ = [
    "ConversationEventFactory",
    "UserMessageFactory",
    "AssistantMessageFactory",
    "ProjectFactory",
    "TranscriptFactory"
]
