#!/usr/bin/env python3
"""
Token Interface - 100% tiktoken framework delegation
SRP: Single responsibility for token counting operations
@COMPOSITION: Works with plain dicts
"""

import tiktoken
from typing import Dict, Any
from ..messages.utils import get_text
from ..settings import settings


def count_tokens(text: str, model: str = None) -> int:
    """100% tiktoken + Pydantic settings: Count tokens in text"""
    if not text:
        return 0
    
    # 100% Pydantic settings delegation: Use configured default model
    model = model or settings.token.default_model
    
    # 100% tiktoken framework delegation
    tokenizer = tiktoken.encoding_for_model(model)
    return len(tokenizer.encode(text))


def analyze_token_usage(session_data: Dict[str, Any], model: str = None) -> Dict[str, int]:
    """Analyze token usage from session dict"""
    # 100% Pydantic settings delegation: Use configured default model
    model = model or settings.token.default_model
    tokenizer = tiktoken.encoding_for_model(model)
    
    messages = session_data.get('messages', [])
    if not messages:
        return {
            'total_tokens': 0,
            'average_tokens': 0,
            'message_count': 0,
            'max_tokens': 0,
            'min_tokens': 0
        }
    
    # Use message utils to extract text
    token_counts = [
        len(tokenizer.encode(get_text(msg)))
        for msg in messages
        if get_text(msg)
    ]
    
    if not token_counts:
        return {
            'total_tokens': 0,
            'average_tokens': 0,
            'message_count': 0,
            'max_tokens': 0,
            'min_tokens': 0
        }
    
    # 100% built-in functions for analysis
    total = sum(token_counts)
    return {
        'total_tokens': total,
        'average_tokens': total // len(token_counts),
        'message_count': len(token_counts),
        'max_tokens': max(token_counts),
        'min_tokens': min(token_counts)
    }


def estimate_cost(total_tokens: int, model: str = None) -> float:
    """100% Pydantic settings: Estimate API cost using configured prices"""
    # 100% Pydantic settings delegation: Use configured default model
    model = model or settings.token.default_model
    
    # 100% Pydantic settings delegation: Use configured cost mapping
    cost_per_1k = settings.token.cost_per_1k
    rate = cost_per_1k.get(model, settings.token.default_cost)
    return (total_tokens / 1000) * rate