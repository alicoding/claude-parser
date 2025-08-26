"""
Unified token service - Eliminates DRY violation across token counting.

SOLID: Single Responsibility - Token counting and pricing only
DDD: Value object for token operations
95/5: Uses tiktoken library for accurate counting
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import tiktoken

from claude_parser.models.usage import UsageInfo


@dataclass(frozen=True)
class TokenPricing:
    """Immutable token pricing configuration."""

    input: Decimal = Decimal("3.00")  # $3 per 1M input tokens
    output: Decimal = Decimal("15.00")  # $15 per 1M output tokens
    cache_write: Decimal = Decimal("3.75")  # $3.75 per 1M cache write
    cache_read: Decimal = Decimal("0.30")  # $0.30 per 1M cache read

    def calculate_cost(self, usage: UsageInfo) -> Decimal:
        """Calculate USD cost from usage info."""
        cost = Decimal("0.0")
        million = Decimal("1_000_000")

        cost += (Decimal(usage.input_tokens) / million) * self.input
        cost += (Decimal(usage.output_tokens) / million) * self.output
        cost += (
            Decimal(usage.cache_creation_input_tokens) / million
        ) * self.cache_write
        cost += (Decimal(usage.cache_read_input_tokens) / million) * self.cache_read

        return cost.quantize(Decimal("0.0001"))


@dataclass(frozen=True)
class TokenCount:
    """Value object for token count with cost calculation."""

    value: int
    pricing: TokenPricing = TokenPricing()
    token_type: str = "input"  # input, output, cache_read, cache_write

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Token count cannot be negative")
        if self.token_type not in ("input", "output", "cache_read", "cache_write"):
            raise ValueError(f"Invalid token type: {self.token_type}")

    @property
    def cost_usd(self) -> Decimal:
        """Calculate cost in USD for this token count."""
        million = Decimal("1_000_000")
        rate = getattr(self.pricing, self.token_type)
        return (Decimal(self.value) / million) * rate


class TokenService:
    """Unified service for token counting and pricing.

    Replaces duplicate implementations in:
    - token_analyzer.py
    - session_analyzer.py
    - analytics/analyzer.py

    Example:
        service = TokenService()
        count = service.count_tokens("Hello world!")
        cost = service.calculate_usage_cost(usage_info)
    """

    def __init__(self, pricing: Optional[TokenPricing] = None):
        """Initialize token service.

        Args:
            pricing: Custom pricing config, defaults to Claude 3.5 Sonnet
        """
        self.pricing = pricing or TokenPricing()
        # Use cl100k_base as approximation for Claude
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for

        Returns:
            Exact token count
        """
        if not text:
            return 0
        return len(self.encoder.encode(text))

    def estimate_tokens_rough(self, text: str) -> int:
        """Fast estimation: ~4 characters per token.

        Use for performance-critical paths where exact count not needed.

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return max(1, len(text) // 4)

    def calculate_usage_cost(self, usage: UsageInfo) -> Decimal:
        """Calculate total cost from usage info.

        Args:
            usage: Usage information with token counts

        Returns:
            Total cost in USD
        """
        return self.pricing.calculate_cost(usage)

    def create_token_count(self, value: int, token_type: str = "input") -> TokenCount:
        """Create a TokenCount value object.

        Args:
            value: Number of tokens
            token_type: Type of tokens (input/output/cache_read/cache_write)

        Returns:
            TokenCount value object
        """
        return TokenCount(value=value, pricing=self.pricing, token_type=token_type)

    def parse_usage_from_message(self, message_data: dict) -> Optional[UsageInfo]:
        """Parse usage info from message data.

        Handles the common pattern of extracting usage from message['usage'].

        Args:
            message_data: Raw message data dict

        Returns:
            UsageInfo if found, None otherwise
        """
        if not isinstance(message_data, dict) or "usage" not in message_data:
            return None

        usage_data = message_data["usage"]
        return UsageInfo(
            input_tokens=usage_data.get("input_tokens", 0),
            output_tokens=usage_data.get("output_tokens", 0),
            cache_creation_input_tokens=usage_data.get(
                "cache_creation_input_tokens", 0
            ),
            cache_read_input_tokens=usage_data.get("cache_read_input_tokens", 0),
            service_tier=usage_data.get("service_tier"),
        )


# Create default service instance for easy imports
default_token_service = TokenService()


# Convenience functions using default service
def count_tokens(text: str) -> int:
    """Count tokens using default service."""
    return default_token_service.count_tokens(text)


def calculate_cost(usage: UsageInfo) -> Decimal:
    """Calculate cost using default service."""
    return default_token_service.calculate_usage_cost(usage)


def estimate_tokens(text: str) -> int:
    """Estimate tokens using default service."""
    return default_token_service.estimate_tokens_rough(text)


__all__ = [
    "TokenPricing",
    "TokenCount",
    "TokenService",
    "default_token_service",
    "count_tokens",
    "calculate_cost",
    "estimate_tokens",
]
