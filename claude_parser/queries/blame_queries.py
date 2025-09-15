"""
Blame queries - @SINGLE_SOURCE_TRUTH for cg blame operations.
@FRAMEWORK_FIRST: 100% DuckDB window functions, no loops.
"""
from typing import List, Dict, Any
from .query_utils import query_all_jsonl


def blame_file(file_path: str, jsonl_paths: List[str]) -> List[Dict[str, Any]]:
    """Find who last modified a file - like git blame.

    Uses DuckDB window functions to find latest modification.
    @UTIL_FIRST: Delegates to query_utils for schema handling.
    """
    query = """
        SELECT
            CAST(uuid AS VARCHAR) as uuid,
            CAST(timestamp AS VARCHAR) as timestamp,
            json_extract_string(toolUseResult, '$.type') as tool_name,
            json_extract_string(toolUseResult, '$.filePath') as file_path
        FROM read_json_auto(?)
        WHERE json_extract_string(toolUseResult, '$.filePath') = ?
            AND toolUseResult IS NOT NULL
        ORDER BY timestamp DESC
        LIMIT 1
    """

    results = query_all_jsonl(jsonl_paths, query, [file_path])
    return results


def blame_all_files(jsonl_paths: List[str]) -> List[Dict[str, Any]]:
    """Get last modifier for all files - 100% framework delegation."""
    query = """
        WITH ranked_ops AS (
            SELECT
                CAST(uuid AS VARCHAR) as uuid,
                CAST(timestamp AS VARCHAR) as timestamp,
                json_extract_string(toolUseResult, '$.type') as tool_name,
                json_extract_string(toolUseResult, '$.filePath') as file_path,
                ROW_NUMBER() OVER (
                    PARTITION BY json_extract_string(toolUseResult, '$.filePath')
                    ORDER BY timestamp DESC
                ) as rn
            FROM read_json_auto(?)
            WHERE toolUseResult IS NOT NULL
                AND json_extract_string(toolUseResult, '$.filePath') IS NOT NULL
        )
        SELECT file_path, uuid, timestamp, tool_name
        FROM ranked_ops
        WHERE rn = 1
        ORDER BY file_path
    """

    results = query_all_jsonl(jsonl_paths, query, [])
    return results