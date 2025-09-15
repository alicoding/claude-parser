#!/usr/bin/env python3
"""
Token Billing Analysis - Cost calculation with proper pricing
@SINGLE_SOURCE_TRUTH: All billing/cost calculations
"""

from typing import Dict, Optional


# Claude pricing per 1M tokens (as of Jan 2025)
CLAUDE_PRICING = {
    'claude-3-opus': {'input': 15.0, 'output': 75.0},
    'claude-3-sonnet': {'input': 3.0, 'output': 15.0},
    'claude-3-haiku': {'input': 0.25, 'output': 1.25},
    'claude-3.5-sonnet': {'input': 3.0, 'output': 15.0},
    'claude-4-opus': {'input': 15.0, 'output': 75.0},
    'claude-4-sonnet': {'input': 3.0, 'output': 15.0},
}


def calculate_session_cost(
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    model: str = 'claude-3.5-sonnet'
) -> Dict[str, float]:
    """
    Calculate session cost based on token usage.
    
    Cache pricing:
    - cache_read: 10% of input price
    - cache_creation: 125% of input price
    
    Returns:
        {
            'input_cost': 0.05,
            'output_cost': 0.25,
            'cache_read_cost': 0.005,
            'cache_creation_cost': 0.0625,
            'total_cost': 0.3675,
            'breakdown': {...}
        }
    """
    # Get base pricing
    pricing = CLAUDE_PRICING.get(model, CLAUDE_PRICING['claude-3.5-sonnet'])
    
    # Calculate costs (per million tokens)
    input_cost = (input_tokens / 1_000_000) * pricing['input']
    output_cost = (output_tokens / 1_000_000) * pricing['output']
    cache_read_cost = (cache_read_tokens / 1_000_000) * (pricing['input'] * 0.1)
    cache_creation_cost = (cache_creation_tokens / 1_000_000) * (pricing['input'] * 1.25)
    
    total_cost = input_cost + output_cost + cache_read_cost + cache_creation_cost
    
    return {
        'input_cost': round(input_cost, 4),
        'output_cost': round(output_cost, 4),
        'cache_read_cost': round(cache_read_cost, 4),
        'cache_creation_cost': round(cache_creation_cost, 4),
        'total_cost': round(total_cost, 4),
        'breakdown': {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cache_read_tokens': cache_read_tokens,
            'cache_creation_tokens': cache_creation_tokens,
            'model': model,
            'rates': pricing
        }
    }