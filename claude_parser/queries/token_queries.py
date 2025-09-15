"""
Token counting queries - @SINGLE_SOURCE_TRUTH for token operations.
Moved from storage/engine.py to follow SRP.
"""
from typing import Dict
from ..storage.engine import get_engine


def count_tokens(jsonl_path: str) -> Dict[str, int]:
    """Count tokens in JSONL using DuckDB aggregation.

    @FRAMEWORK_FIRST: 100% SQL delegation, no loops.
    """
    engine = get_engine()
    result = engine.execute("""
        WITH messages AS (
            SELECT * FROM read_json_auto(?)
        )
        SELECT
            COALESCE(SUM(CASE
                WHEN type = 'assistant'
                THEN CAST(json_extract_string(message, '$.usage.input_tokens') AS INT) +
                     CAST(json_extract_string(message, '$.usage.output_tokens') AS INT)
                ELSE 0
            END), 0) as assistant_tokens,
            COALESCE(SUM(CASE
                WHEN type = 'user'
                THEN LENGTH(json_extract_string(message, '$.content')) / 4
                ELSE 0
            END), 0) as user_tokens
        FROM messages
    """, [jsonl_path]).fetchone()

    return {
        'assistant_tokens': result[0],
        'user_tokens': result[1],
        'total_context': result[0] + result[1]
    }