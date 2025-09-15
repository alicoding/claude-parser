#!/usr/bin/env python3
"""
Operations Domain - @BOUNDED_CONTEXT_ISOLATION
SRP: File operations and diffing operations only
"""

from .core import (
    restore_file_content, generate_file_diff, compare_files, backup_file,
    restore_file_from_jsonl, restore_folder_from_jsonl
)

__all__ = [
    'restore_file_content', 'generate_file_diff', 'compare_files', 'backup_file',
    'restore_file_from_jsonl', 'restore_folder_from_jsonl'
]