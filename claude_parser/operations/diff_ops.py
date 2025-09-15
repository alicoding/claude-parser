#!/usr/bin/env python3
"""
Diff operations - generate diffs between files
@SINGLE_SOURCE_TRUTH: Separated from core.py for LOC compliance
@FRAMEWORK_FIRST: 100% difflib delegation
"""
import difflib
from typing import Optional
from pathlib import Path


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