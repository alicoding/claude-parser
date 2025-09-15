"""
Reflog queries - @SINGLE_SOURCE_TRUTH for cg reflog operations.
@FRAMEWORK_FIRST: 100% DuckDB SQL, no custom loops.
"""
from typing import List, Dict, Any
from .query_utils import query_all_jsonl


def get_reflog(jsonl_paths: List[str], limit: int = 50) -> List[Dict[str, Any]]:
    """Get all operations history - like git reflog.

    Shows all tool operations across all sessions.
    @UTIL_FIRST: Delegates to query_utils for schema handling.
    """
    query = """
        SELECT
            CAST(uuid AS VARCHAR) as uuid,
            CAST(timestamp AS VARCHAR) as timestamp,
            json_extract_string(toolUseResult, '$.type') as tool_name,
            json_extract_string(toolUseResult, '$.filePath') as file_path,
            CAST(type AS VARCHAR) as operation_type
        FROM read_json_auto(?)
        WHERE toolUseResult IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 1000
    """

    # Get all results then limit in Python (since LIMIT is per-file)
    results = query_all_jsonl(jsonl_paths, query)

    # Sort by timestamp and limit
    results.sort(key=lambda x: x[1] if x[1] else '', reverse=True)
    return results[:limit]


def get_file_history(file_path: str, jsonl_paths: List[str]) -> List[Dict[str, Any]]:
    """Get complete history of a specific file."""
    engine = get_engine()
    unions = " UNION ALL ".join([
        f"SELECT * FROM read_json_auto('{path}')"
        for path in jsonl_paths
    ])

    return engine.execute(f"""
        WITH all_messages AS ({unions})
        SELECT
            uuid,
            timestamp,
            tool_name,
            tool_input,
            tool_use_result
        FROM all_messages
        WHERE json_extract_string(tool_input, '$.file_path') = ?
        ORDER BY timestamp ASC
    """, [file_path]).fetchall()