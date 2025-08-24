"""
Content-based message filter.

SOLID: Single Responsibility - Only content filtering.
95/5: Using toolz for functional operations.
"""

from ...models import Message


class ContentFilter:
    """Filter messages by content."""
    
    def __init__(self, query: str, case_sensitive: bool = False):
        """Initialize with search query."""
        self.query = query if case_sensitive else query.lower()
        self.case_sensitive = case_sensitive
    
    def matches(self, message: Message) -> bool:
        """Check if message content matches query."""
        content = message.text_content
        if not self.case_sensitive:
            content = content.lower()
        return self.query in content