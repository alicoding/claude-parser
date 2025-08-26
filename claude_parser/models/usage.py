"""
Token usage model based on discoveries from 41,085 real messages.

SOLID: Single Responsibility - Token usage tracking only
DDD: Value object for token usage
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CacheCreation(BaseModel):
    """Cache creation breakdown."""

    ephemeral_5m_input_tokens: int = Field(0, ge=0, alias="ephemeral_5m_input_tokens")
    ephemeral_1h_input_tokens: int = Field(0, ge=0, alias="ephemeral_1h_input_tokens")


class ServerToolUse(BaseModel):
    """Server-side tool usage tracking."""

    web_search_requests: int = Field(0, ge=0, alias="web_search_requests")


class UsageInfo(BaseModel):
    """Complete token usage information from Claude API.

    Discovered from analyzing 17,064 assistant messages.
    """

    # Core token counts
    input_tokens: int = Field(0, ge=0, alias="input_tokens")
    output_tokens: int = Field(0, ge=0, alias="output_tokens")

    # Cache usage (critical for token economy!)
    cache_creation_input_tokens: int = Field(
        0, ge=0, alias="cache_creation_input_tokens"
    )
    cache_read_input_tokens: int = Field(0, ge=0, alias="cache_read_input_tokens")

    # Detailed cache breakdown (optional)
    cache_creation: Optional[CacheCreation] = Field(None, alias="cache_creation")

    # Service tier
    service_tier: Optional[str] = Field(None, alias="service_tier")

    # Tool usage
    server_tool_use: Optional[ServerToolUse] = Field(None, alias="server_tool_use")

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens processed."""
        return (
            self.input_tokens
            + self.output_tokens
            + self.cache_creation_input_tokens
            + self.cache_read_input_tokens
        )

    @property
    def cache_efficiency(self) -> float:
        """Calculate cache hit ratio (0.0 to 1.0)."""
        total_input = self.input_tokens + self.cache_read_input_tokens
        if total_input == 0:
            return 0.0
        return self.cache_read_input_tokens / total_input

    @property
    def is_cached(self) -> bool:
        """Check if this response used cache."""
        return self.cache_read_input_tokens > 0

    @property
    def cache_savings(self) -> int:
        """Calculate tokens saved by cache usage."""
        return self.cache_read_input_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Export usage info as dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_creation_input_tokens": self.cache_creation_input_tokens,
            "cache_read_input_tokens": self.cache_read_input_tokens,
            "total_tokens": self.total_tokens,
            "cache_efficiency": self.cache_efficiency,
            "cache_savings": self.cache_savings,
            "service_tier": self.service_tier,
        }
