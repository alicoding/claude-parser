"""
Find queries - @SINGLE_SOURCE_TRUTH for cg find operations.
@FRAMEWORK_FIRST: 100% DuckDB SQL, no custom loops.
"""
from typing import List, Dict, Any
from .query_utils import query_with_sort, query_all_jsonl


def find_files(pattern: str, jsonl_paths: List[str]) -> List[Dict[str, Any]]:
    """Find files matching pattern across all messages.

    Like: git log --all --grep
    @UTIL_FIRST: Delegates to query_utils for schema handling.
    """
    query = """
        SELECT DISTINCT
            CAST(uuid AS VARCHAR) as uuid,
            json_extract_string(toolUseResult, '$.filePath') as file_path,
            CAST(timestamp AS VARCHAR) as timestamp,
            json_extract_string(toolUseResult, '$.type') as tool_name
        FROM read_json_auto(?)
        WHERE json_extract_string(toolUseResult, '$.filePath') LIKE ?
            AND toolUseResult IS NOT NULL
    """

    return query_with_sort(
        jsonl_paths,
        query,
        [f'%{pattern}%'],
        sort_key=lambda x: x[2] if x[2] else ''
    )


def find_by_tool(tool_name: str, jsonl_paths: List[str]) -> List[Dict[str, Any]]:
    """Find all uses of a specific tool."""
    query = """
        SELECT
            CAST(uuid AS VARCHAR) as uuid,
            CAST(timestamp AS VARCHAR) as timestamp,
            tool_name,
            tool_input
        FROM read_json_auto(?)
        WHERE tool_name = ?
    """

    results = query_all_jsonl(jsonl_paths, query, [tool_name])
    # Sort by timestamp descending
    results.sort(key=lambda x: x[1] if x[1] else '', reverse=True)
    return results