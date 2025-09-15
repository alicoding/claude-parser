#!/usr/bin/env python3
"""
Token Status API - One-liner for real-time token tracking
Uses actual Claude API usage data from JSONL instead of tiktoken estimates
@COMPOSITION: Works with plain dicts
"""

from typing import Dict, Any, Optional
from ..main import load_latest_session
from ..messages.utils import get_token_usage


def token_status(limit: int = 175000, from_checkpoint: bool = False) -> Dict[str, float]:
    """
    One-liner for complete token status using Claude's actual usage data.
    
    Args:
        limit: Context window limit (default 175K for Claude Sonnet)
        from_checkpoint: Count from last checkpoint instead of session start
    
    Returns:
        {
            'current': 45000,      # Current tokens used
            'limit': 175000,       # Context window limit  
            'percentage': 25.7,    # Percentage used
            'remaining': 130000,   # Tokens remaining
            'estimated_messages': 325  # Estimated remaining messages
        }
    """
    session_data = load_latest_session()
    if not session_data:
        return {
            'current': 0,
            'limit': limit,
            'percentage': 0.0,
            'remaining': limit,
            'estimated_messages': 0
        }
    
    # Calculate from Claude's actual usage data
    current = _calculate_session_tokens(session_data, from_checkpoint)
    percentage = (current / limit) * 100 if limit > 0 else 0
    remaining = max(0, limit - current)
    estimated_messages = remaining // 400  # Average message ~400 tokens
    
    return {
        'current': current,
        'limit': limit,
        'percentage': round(percentage, 1),
        'remaining': remaining,
        'estimated_messages': estimated_messages
    }


def _calculate_session_tokens(session_data: Dict[str, Any], from_checkpoint: bool = False) -> int:
    """Calculate context window tokens from session dict"""
    messages = session_data.get('messages', [])
    if not messages:
        return 0
    
    if from_checkpoint:
        # TODO: Implement checkpoint-based calculation when needed
        # For now, use all messages
        pass
    
    # Sum tokens from all messages
    # Context window = input + output (cache tokens FREE for context limit)
    total = 0
    for msg in messages:
        usage = get_token_usage(msg)
        if usage:
            total += usage.get('input_tokens', 0) + usage.get('output_tokens', 0)
    
    return total