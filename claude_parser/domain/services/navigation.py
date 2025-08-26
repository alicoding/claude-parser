"""
Conversation navigation service.

SOLID: Single Responsibility - Only navigation operations.
DDD: Domain Service - Complex navigation logic.
95/5: Using libraries (networkx, pendulum, toolz).
"""

from typing import TYPE_CHECKING, List, Optional

import networkx as nx
import pendulum
from toolz import filter as toolz_filter
from toolz import map as toolz_map
from toolz import pipe

if TYPE_CHECKING:
    from ...models import Message
    from ..entities.conversation import Conversation


class NavigationService:
    """Service for navigating through conversation messages."""

    def __init__(self, conversation: "Conversation"):
        """Initialize with conversation to navigate."""
        self.conversation = conversation
        self._build_indices()

    def _build_indices(self):
        """Build navigation indices for O(1) lookups."""
        messages = self.conversation._messages

        # Build UUID index using toolz
        self._uuid_index = pipe(
            messages,
            lambda msgs: toolz_filter(lambda m: hasattr(m, "uuid"), msgs),
            lambda msgs: toolz_map(lambda m: (m.uuid, m), msgs),
            dict,
        )

        # Build UUID to position index
        self._uuid_to_index = pipe(
            enumerate(messages),
            lambda items: toolz_filter(lambda x: hasattr(x[1], "uuid"), items),
            lambda items: toolz_map(lambda x: (x[1].uuid, x[0]), items),
            dict,
        )

    def get_by_uuid(self, uuid: str) -> Optional["Message"]:
        """Get message by UUID with O(1) lookup."""
        return self._uuid_index.get(uuid)

    def get_surrounding(
        self, uuid: str, before: int = 2, after: int = 2
    ) -> List["Message"]:
        """Get messages surrounding a specific message."""
        target_idx = self._uuid_to_index.get(uuid, -1)

        if target_idx == -1:
            return []

        messages = self.conversation._messages
        start_idx = max(0, target_idx - before)
        end_idx = min(len(messages), target_idx + after + 1)

        return messages[start_idx:end_idx]

    def get_messages_between_timestamps(
        self, start: Optional[str], end: Optional[str]
    ) -> List["Message"]:
        """Get messages between two timestamps using pendulum."""
        if not start or not end:
            return []

        # Use pendulum for robust timestamp handling
        start_dt = pendulum.parse(start) if isinstance(start, str) else start
        end_dt = pendulum.parse(end) if isinstance(end, str) else end

        # Use functional filtering with toolz
        return pipe(
            self.conversation._messages,
            lambda msgs: toolz_filter(
                lambda m: (
                    hasattr(m, "timestamp")
                    and m.timestamp
                    and start_dt
                    <= (
                        pendulum.parse(m.timestamp)
                        if isinstance(m.timestamp, str)
                        else m.timestamp
                    )
                    <= end_dt
                ),
                msgs,
            ),
            list,
        )

    def get_thread_from(self, uuid: str) -> List["Message"]:
        """Get thread using NetworkX for graph operations."""
        # Build conversation graph
        G = nx.DiGraph()

        # Add nodes using functional approach
        pipe(
            self.conversation._messages,
            lambda msgs: toolz_filter(lambda m: hasattr(m, "uuid") and m.uuid, msgs),
            lambda msgs: toolz_map(lambda m: G.add_node(m.uuid, data=m), msgs),
            list,
        )

        # Add edges for parent-child relationships
        pipe(
            self.conversation._messages,
            lambda msgs: toolz_filter(
                lambda m: (
                    hasattr(m, "uuid")
                    and hasattr(m, "parent_uuid")
                    and m.parent_uuid
                    and m.parent_uuid in G
                ),
                msgs,
            ),
            lambda msgs: toolz_map(lambda m: G.add_edge(m.parent_uuid, m.uuid), msgs),
            list,
        )

        if uuid not in G:
            return []

        # Get thread using NetworkX
        thread_uuids = [uuid] + list(nx.descendants(G, uuid))

        return pipe(
            thread_uuids,
            lambda uuids: toolz_map(lambda u: G.nodes[u]["data"], uuids),
            list,
        )
