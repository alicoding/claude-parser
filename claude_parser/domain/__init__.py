"""
Domain layer - Core business logic.

Following DDD with proper separation:
- entities: Core domain models
- value_objects: Immutable value types
- services: Domain operations
- filters: Message filtering strategies
- interfaces: Domain contracts
"""

# Entities
from .entities import Conversation

# Filters
from .filters import ContentFilter, ErrorFilter, TypeFilter

# Interfaces
from .interfaces import MessageFilter, MessageRepository

# Services
from .services import ConversationAnalyzer, NavigationService

# Value Objects
from .value_objects import ConversationMetadata

__all__ = [
    # Core entity
    "Conversation",
    # Value objects
    "ConversationMetadata",
    # Services
    "ConversationAnalyzer",
    "NavigationService",
    # Filters
    "ContentFilter",
    "TypeFilter",
    "ErrorFilter",
    # Interfaces
    "MessageFilter",
    "MessageRepository",
]
