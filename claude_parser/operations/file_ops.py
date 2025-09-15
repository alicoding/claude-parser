#!/usr/bin/env python3
"""
File operations - atomic file operations using pyfilesystem2
@SINGLE_SOURCE_TRUTH: Separated from core.py for LOC compliance
@FRAMEWORK_FIRST: 100% pyfilesystem2 delegation
"""
from typing import Optional
from pathlib import Path

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