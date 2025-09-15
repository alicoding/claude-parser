#!/usr/bin/env python3
"""
Billing Analytics - Cost calculation
@COMPOSITION: Works with plain dicts
"""

from typing import Dict, Any
from litellm import completion_cost
from more_itertools import first
from ..messages.utils import get_token_usage, get_model
from .litellm_adapter import to_litellm_response


def calculate_session_cost(from_checkpoint: bool = False) -> Dict[str, Any]:
    """Calculate billing cost for current session.
    
    Args:
        from_checkpoint: If True, calculate from last checkpoint
                        If False, calculate from session start
    
    Returns:
        Dict with total cost and token breakdown
    """
    from ..main import load_latest_session
    
    session_data = load_latest_session()
    if not session_data:
        return _empty_cost_result()
    
    messages = session_data.get('messages', [])
    
    # Filter to assistant messages with model info
    assistant_messages = [
        m for m in messages 
        if (m.get('type') == 'assistant' or m.get('role') == 'assistant') 
        and get_model(m)
    ]
    
    if not assistant_messages:
        return _empty_cost_result()
    
    # Calculate cost using litellm
    responses = list(map(to_litellm_response, assistant_messages))
    total_cost = sum(map(completion_cost, responses))
    
    # Calculate token totals
    input_total = 0
    cache_total = 0
    output_total = 0
    
    for msg in assistant_messages:
        usage = get_token_usage(msg)
        input_total += usage.get('input_tokens', 0)
        cache_total += usage.get('cache_read_input_tokens', 0)
        output_total += usage.get('output_tokens', 0)
    
    return {
        'total_cost': round(total_cost, 4),
        'input_tokens': input_total,
        'cache_tokens': cache_total,
        'output_tokens': output_total,
        'model': get_model(first(assistant_messages)),
        'currency': 'USD'
    }


def _empty_cost_result() -> Dict[str, Any]:
    """Return empty cost result structure"""
    return {
        'total_cost': 0.0,
        'input_tokens': 0,
        'cache_tokens': 0,
        'output_tokens': 0,
        'model': None,
        'currency': 'USD'
    }