#!/usr/bin/env python3
"""
Operations Interface - 100% framework delegation for file operations
SRP: Single responsibility for file restoration and diffing
"""

import difflib
import json
from typing import Optional, Dict, List

# Lazy import to avoid warning
def get_fs():
    from fs import open_fs
    return open_fs


def restore_file_content(file_path: str, backup_content: bytes) -> bool:
    """Use pyfilesystem2 for atomic file operations"""
    try:
        open_fs = get_fs()
        with open_fs('/') as filesystem:
            import fs.path
            filesystem.makedirs(fs.path.dirname(file_path), recreate=True)
            filesystem.writebytes(file_path, backup_content)
        return True
    except Exception:
        return False


def generate_file_diff(content1: str, content2: str, label1: str = "before", label2: str = "after") -> str:
    """100% difflib delegation: Generate unified diff between two text contents"""
    lines1 = content1.splitlines(keepends=True)
    lines2 = content2.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        lines1, lines2,
        fromfile=label1,
        tofile=label2,
        n=3
    )
    
    return ''.join(diff)


def compare_files(file_path1: str, file_path2: str) -> Optional[str]:
    """100% framework delegation: Compare two files and return diff"""
    try:
        path1, path2 = Path(file_path1), Path(file_path2)
        
        if not path1.exists() or not path2.exists():
            return None
            
        content1 = path1.read_text(encoding='utf-8', errors='ignore')
        content2 = path2.read_text(encoding='utf-8', errors='ignore')
        
        return generate_file_diff(content1, content2, str(path1), str(path2))
    except (OSError, IOError):
        return None


def backup_file(file_path: str, backup_suffix: str = ".bak") -> Optional[str]:
    """100% pathlib delegation: Create backup of file"""
    try:
        source = Path(file_path)
        if not source.exists():
            return None

        backup_path = source.with_suffix(source.suffix + backup_suffix)
        backup_path.write_bytes(source.read_bytes())
        return str(backup_path)
    except (OSError, IOError):
        return None


def restore_file_from_jsonl(jsonl_path: str, checkpoint_uuid: str, file_path: str) -> bool:
    """Restore single file from JSONL - looks for last good version"""
    from ..storage.jsonl_engine import query_jsonl

    # Find ALL versions of this file, ordered by time (newest first)
    results = query_jsonl(jsonl_path, f"""
        toolUseResult LIKE '%"filePath":"{file_path}"%'
        AND toolUseResult IS NOT NULL
        ORDER BY timestamp DESC
    """)

    # Find the most recent version that's not the current bad one
    for row in results:
        try:
            # Parse the JSON string (toolUseResult is typically last column)
            tool_result_str = None
            for item in reversed(row):
                if isinstance(item, str) and '"filePath"' in item:
                    tool_result_str = item
                    break

            if not tool_result_str:
                continue

            tool_result = json.loads(tool_result_str)

            # Skip if this is the current checkpoint (the bad edit)
            if str(row[11]) == checkpoint_uuid:  # uuid is typically column 11
                continue

            # Found a good version
            if tool_result.get('filePath') == file_path and 'content' in tool_result:
                return restore_file_content(file_path, tool_result['content'].encode('utf-8'))
        except:
            continue
    return False


def restore_folder_from_jsonl(jsonl_path: str, checkpoint_uuid: str, folder_path: str) -> List[str]:
    """Restore all files in folder using fs for batch operations"""
    from ..storage.jsonl_engine import query_jsonl

    # Normalize prefix for both relative and absolute paths
    import os
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
                # Get toolUseResult from the row (it's the last non-null string column typically)
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