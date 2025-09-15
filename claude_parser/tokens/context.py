#!/usr/bin/env python3
"""
Context Window Calculation - Proper user/assistant token separation
@SINGLE_SOURCE_TRUTH: Context window calculation logic
"""

from typing import Dict, Optional
from pathlib import Path
from ..storage.engine import get_engine
from ..main import load_latest_session


def calculate_context_window(jsonl_path: Optional[str] = None) -> Dict[str, int]:
    """
    Calculate context window usage with proper user/assistant separation.
    
    Key insight: User messages don't have usage field in JSONL!
    - Assistant messages: Have exact token counts in usage field
    - User messages: Must estimate from content length
    
    Returns:
        {
            'assistant_tokens': 53000,   # From usage field
            'user_tokens': 120000,        # Estimated from content
            'total_context': 173000,      # Sum of both
            'percentage': 96.1            # Of 180K limit
        }
    """
    if not jsonl_path:
        # Get latest session path
        session = load_latest_session()
        if not session or not session.raw_data:
            return {
                'assistant_tokens': 0,
                'user_tokens': 0,
                'total_context': 0,
                'percentage': 0.0
            }
        # Extract path from raw data (would need to track this)
        jsonl_path = getattr(session, 'source_path', None)
        if not jsonl_path:
            # Fallback to discovery
            from ..discovery import discover_current_project_files
            files = discover_current_project_files()
            jsonl_path = str(files[0]) if files else None
    
    if not jsonl_path or not Path(jsonl_path).exists():
        return {
            'assistant_tokens': 0,
            'user_tokens': 0,
            'total_context': 0,
            'percentage': 0.0
        }
    
    # @SINGLE_SOURCE_TRUTH: Delegate to queries module
    from ..queries.token_queries import count_tokens
    result = count_tokens(jsonl_path)
    
    # Calculate percentage (180K is Claude's context limit)
    context_limit = 180000
    percentage = (result['total_context'] / context_limit * 100) if context_limit > 0 else 0
    
    return {
        'assistant_tokens': result['assistant_tokens'],
        'user_tokens': result['user_tokens'],
        'total_context': result['total_context'],
        'percentage': round(percentage, 1)
    }