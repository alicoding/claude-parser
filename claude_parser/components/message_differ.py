"""
MessageDiffer micro-component - Detect new messages between conversation states.

95/5 principle: Simple list comparison, framework handles data structures.
Size: ~12 LOC (LLM-readable in single context)
"""

from typing import List, Optional
from ..core.resources import ResourceManager
from ..models import Message
from ..domain.entities.conversation import Conversation


class MessageDiffer:
    """Micro-component: Find new messages between conversation states."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def find_new_messages(
        self,
        current_conv: Conversation,
        previous_conv: Optional[Conversation] = None,
        after_uuid: Optional[str] = None
    ) -> List[Message]:
        """Find new messages - simple comparison logic."""
        if previous_conv is None:
            # First load - apply UUID checkpoint if specified
            messages = current_conv.messages
            if after_uuid:
                # Find messages after specified UUID
                checkpoint_found = False
                filtered_messages = []
                for msg in messages:
                    if msg.uuid == after_uuid:
                        checkpoint_found = True
                        continue
                    if checkpoint_found:
                        filtered_messages.append(msg)
                return filtered_messages
            return messages
        else:
            # Find truly new messages since last conversation
            if len(current_conv.messages) > len(previous_conv.messages):
                return current_conv.messages[len(previous_conv.messages):]
            return []
