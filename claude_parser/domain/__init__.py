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

# Value Objects
from .value_objects import ConversationMetadata

# Services
from .services import ConversationAnalyzer, NavigationService

# Filters
from .filters import ContentFilter, TypeFilter, ErrorFilter

# Interfaces
from .interfaces import MessageFilter, MessageRepository

__all__ = [
    # Core entity
    'Conversation',
    # Value objects
    'ConversationMetadata',
    # Services
    'ConversationAnalyzer',
    'NavigationService',
    # Filters
    'ContentFilter',
    'TypeFilter', 
    'ErrorFilter',
    # Interfaces
    'MessageFilter',
    'MessageRepository',
]