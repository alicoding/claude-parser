#!/usr/bin/env python3
"""
Restore operations - restore files from JSONL history
@SINGLE_SOURCE_TRUTH: Separated from core.py for LOC compliance
@FRAMEWORK_FIRST: DuckDB and fs delegation
"""
import json
from typing import List, Optional, Any
from .file_ops import restore_file_content


def _extract_tool_result(row: List[Any]) -> Optional[dict]:
    """Extract and parse toolUseResult from query row"""
    for item in reversed(row):
        if isinstance(item, str) and '"filePath"' in item:
            try:
                return json.loads(item)
            except:
                continue
    return None


def restore_file_from_jsonl(jsonl_path: str, checkpoint_uuid: str, file_path: str) -> bool:
    """Restore single file from JSONL - looks for last good version"""
    from ..storage.jsonl_engine import query_jsonl

    # Find ALL versions of this file
    results = query_jsonl(jsonl_path, f"""
        toolUseResult LIKE '%"filePath":"{file_path}"%'
        AND toolUseResult IS NOT NULL
        ORDER BY timestamp DESC
    """)

    for row in results:
        # Skip current checkpoint
        if str(row[11]) == checkpoint_uuid:
            continue

        tool_result = _extract_tool_result(row)
        if tool_result and tool_result.get('filePath') == file_path and 'content' in tool_result:
            return restore_file_content(file_path, tool_result['content'].encode('utf-8'))

    return False


def restore_folder_from_jsonl(jsonl_path: str, checkpoint_uuid: str, folder_path: str) -> List[str]:
    """Restore all files in folder using fs for batch operations"""
    from ..storage.jsonl_engine import query_jsonl
    import os

    # Normalize prefix for both relative and absolute paths
    prefix = folder_path.rstrip('/') + '/'
    if not prefix.startswith('/'):
        prefix = os.path.abspath(prefix).rstrip('/') + '/'

    # Query with DuckDB - let it handle the SQL
    results = query_jsonl(jsonl_path, f"""
        timestamp < (SELECT timestamp FROM read_json_auto('{jsonl_path}') WHERE uuid = '{checkpoint_uuid}')
        AND toolUseResult LIKE '%"filePath":"%{os.path.basename(folder_path)}/%'
        AND toolUseResult IS NOT NULL
        ORDER BY timestamp DESC
    """)

    restored = []
    seen_files = set()

    # Use fs for batch writing
    open_fs = get_fs()
    with open_fs('/') as filesystem:
        for row in results:
            try:
                # Get toolUseResult from the row
                tool_result_str = None
                for item in reversed(row):
                    if isinstance(item, str) and item.startswith('{'):
                        tool_result_str = item
                        break

                if not tool_result_str:
                    continue

                data = json.loads(tool_result_str)
                file_path = data.get('filePath', '')

                # Check if file matches our folder
                if file_path not in seen_files and prefix in file_path:
                    seen_files.add(file_path)
                    import fs.path
                    filesystem.makedirs(fs.path.dirname(file_path), recreate=True)
                    filesystem.writetext(file_path, data.get('content', ''))
                    restored.append(file_path)
            except Exception:
                continue

    return restored