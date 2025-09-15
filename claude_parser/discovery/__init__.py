#!/usr/bin/env python3
"""
Discovery Domain - @BOUNDED_CONTEXT_ISOLATION
SRP: File discovery and project structure analysis only
"""

from .core import discover_claude_files, group_by_projects, analyze_project_structure, discover_current_project_files

__all__ = ['discover_claude_files', 'group_by_projects', 'analyze_project_structure', 'discover_current_project_files']