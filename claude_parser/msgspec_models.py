"""
SOLID/DDD Base Message Structure with msgspec Framework.

DRY: Single base structure shared by all message types
SOLID: Domain logic separated from serialization
Framework: msgspec handles parsing, we keep business logic
"""

import msgspec
from typing import Optional, Union
from abc import abstractmethod


# Base fields shared across all messages (DRY principle)
# These will be included in each message type individually
# to avoid inheritance issues with msgspec tags

from typing import Optional


# Import actual message classes
from .models.user import UserMessage
from .models.assistant import AssistantMessage

# Canonical msgspec Union type for polymorphic decoding
Message = Union[
    UserMessage,
    AssistantMessage,
    # Add other message types as they're migrated
]
