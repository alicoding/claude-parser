"""
Token counting queries - @SINGLE_SOURCE_TRUTH for token operations.
Moved from storage/engine.py to follow SRP.
"""
from typing import Dict
from ..storage.engine import get_engine


def count_tokens(jsonl_path: str) -> Dict[str, int]:
    """Count tokens after last compact boundary matching UI calculation.

    @FRAMEWORK_FIRST: 100% SQL delegation, no loops.
    UI counts: compact summary content + user message content + assistant cumulative usage
    """
    engine = get_engine()

    # First find the last compact summary position
    compact_result = engine.execute("""
        WITH messages AS (
            SELECT *, ROW_NUMBER() OVER () as row_num
            FROM read_json_auto(?)
        )
        SELECT MAX(row_num) as last_compact_row
        FROM messages
        WHERE isCompactSummary = true
    """, [jsonl_path]).fetchone()

    last_compact_row = compact_result[0] if compact_result and compact_result[0] else 0

    # Count tokens from compact summary and user messages (estimated by length/4)
    content_result = engine.execute("""
        WITH messages AS (
            SELECT *, ROW_NUMBER() OVER () as row_num
            FROM read_json_auto(?)
        )
        SELECT
            COALESCE(SUM(
                CASE
                    WHEN isCompactSummary = true THEN LENGTH(json_extract_string(message, '$.content')) / 4
                    WHEN type = 'user' THEN LENGTH(json_extract_string(message, '$.content')) / 4
                    ELSE 0
                END
            ), 0) as content_tokens
        FROM messages
        WHERE row_num >= ?
    """, [jsonl_path, last_compact_row]).fetchone()

    # Get assistant cumulative usage tokens
    usage_result = engine.execute("""
        WITH messages AS (
            SELECT *, ROW_NUMBER() OVER () as row_num
            FROM read_json_auto(?)
        )
        SELECT
            COALESCE(SUM(
                COALESCE(CAST(json_extract_string(message, '$.usage.input_tokens') AS INT), 0) +
                COALESCE(CAST(json_extract_string(message, '$.usage.cache_read_input_tokens') AS INT), 0)
            ), 0) as input_tokens,
            COALESCE(SUM(
                COALESCE(CAST(json_extract_string(message, '$.usage.output_tokens') AS INT), 0)
            ), 0) as output_tokens
        FROM messages
        WHERE type = 'assistant' AND row_num > ?
    """, [jsonl_path, last_compact_row]).fetchone()

    content_tokens = int(content_result[0]) if content_result else 0
    input_tokens = usage_result[0] if usage_result else 0
    output_tokens = usage_result[1] if usage_result else 0

    return {
        'assistant_tokens': output_tokens,
        'user_tokens': input_tokens,
        'total_context': content_tokens + input_tokens + output_tokens
    }