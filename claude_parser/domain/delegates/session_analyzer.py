"""
Session analysis delegate.

SOLID: Single Responsibility - Only session boundary analysis.
95/5: Using functional approaches.
"""

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...models import Message


class SessionAnalyzer:
    """
    Handles session boundary detection and analysis.
    Extracted from Conversation to follow SRP.
    """

    def __init__(self, messages: List["Message"]):
        """Initialize with messages to analyze."""
        self._messages = messages

    def get_boundaries(self) -> List[int]:
        """
        Get indices where session ID changes.

        Returns:
            List of indices marking session boundaries.
            First message (index 0) is always included as a boundary.
        """
        if not self._messages:
            return []

        boundaries = [0]  # First message is always a boundary
        current_session = getattr(self._messages[0], "session_id", None)

        for i, msg in enumerate(self._messages[1:], 1):
            msg_session = getattr(msg, "session_id", None)
            if msg_session != current_session:
                boundaries.append(i)
                current_session = msg_session

        return boundaries

    def get_sessions(self) -> List[List["Message"]]:
        """
        Split messages into separate sessions.

        Returns:
            List of message lists, one per session.
        """
        boundaries = self.get_boundaries()

        if not boundaries:
            return []

        sessions = []
        for i in range(len(boundaries)):
            start = boundaries[i]
            end = boundaries[i + 1] if i + 1 < len(boundaries) else len(self._messages)
            sessions.append(self._messages[start:end])

        return sessions

    def get_session_count(self) -> int:
        """Get number of distinct sessions."""
        return len(self.get_boundaries())

    def get_messages_for_session(self, session_id: str) -> List["Message"]:
        """Get all messages for a specific session ID."""
        return [
            msg for msg in self._messages
            if getattr(msg, "session_id", None) == session_id
        ]
