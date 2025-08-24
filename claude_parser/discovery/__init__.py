"""
Discovery domain - Find Claude Code transcript paths.

95/5 Principle:
- Simple factory function for current CWD
- Rich options for advanced discovery patterns
"""

from .transcript_finder import (
    find_current_transcript, 
    find_transcript_for_cwd, 
    list_all_projects,
    find_project_by_original_path,
    find_project_by_encoded_name,
)

__all__ = [
    "find_current_transcript", 
    "find_transcript_for_cwd",
    "list_all_projects",
    "find_project_by_original_path",
    "find_project_by_encoded_name",
]