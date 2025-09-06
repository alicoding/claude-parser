"""
TokenCounter micro-component - Text token counting.

95/5 principle: tiktoken does all the work, we just coordinate.
Size: ~12 LOC (LLM-readable in single context)
"""

from ..core.resources import ResourceManager


class TokenCounter:
    """Micro-component: Count tokens using framework."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self._encoder = resources.get_token_encoder()

    def count(self, text: str) -> int:
        """Count tokens - framework does everything."""
        return len(self._encoder.encode(text))
