#!/usr/bin/env python3
"""
Operations Interface - 100% framework delegation for file operations
@SINGLE_SOURCE_TRUTH: Main interface delegates to specialized modules
@LOC_ENFORCEMENT: <80 LOC by splitting into modules
"""

# Re-export from specialized modules for backwards compatibility
from .file_ops import restore_file_content, backup_file
from .diff_ops import generate_file_diff, compare_files
from .restore_ops import restore_file_from_jsonl, restore_folder_from_jsonl

__all__ = [
    'restore_file_content',
    'backup_file',
    'generate_file_diff',
    'compare_files',
    'restore_file_from_jsonl',
    'restore_folder_from_jsonl'
]