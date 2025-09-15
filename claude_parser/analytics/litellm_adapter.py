#!/usr/bin/env python3
"""
LiteLLM Adapter - Convert dicts to litellm format
@SINGLE_SOURCE_TRUTH: One place for litellm conversion
"""

from typing import Dict, Any
from litellm import ModelResponse, Usage
from ..messages.utils import get_token_usage, get_model


def to_litellm_response(msg: Dict[str, Any]) -> ModelResponse:
    """Convert message dict to litellm ModelResponse"""
    usage_data = get_token_usage(msg)
    usage = Usage(
        prompt_tokens=usage_data.get('input_tokens', 0),
        completion_tokens=usage_data.get('output_tokens', 0),
        total_tokens=usage_data.get('input_tokens', 0) + usage_data.get('output_tokens', 0),
        prompt_tokens_details={'cached_tokens': usage_data.get('cache_read_input_tokens', 0)}
    )
    return ModelResponse(model=get_model(msg), usage=usage)