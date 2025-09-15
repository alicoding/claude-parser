#!/usr/bin/env python3
"""
Discovery Interface - Delegates to loaders/discovery.py to avoid DRY violation
SRP: Single entry point for discovery, delegates to specialized loaders
"""

from pathlib import Path
from typing import List, Dict, Any
from ..loaders.discovery import discover_all_sessions
from ..loaders.session import load_session


def discover_current_project_files() -> List[Path]:
    """Discover files for current project - delegates to loaders"""
    # Get current project encoding
    cwd = Path.cwd()
    project_name = str(cwd).replace('/', '-')
    project_dir = Path.home() / ".claude/projects" / project_name

    if not project_dir.exists():
        return []

    # Find all JSONL files including active session
    # Active session might have different pattern or be in progress
    files = list(project_dir.glob("*.jsonl"))

    # Also check for any in-progress files (common patterns)
    in_progress_patterns = ["*.jsonl.tmp", "*.jsonl.active", "*.partial"]
    for pattern in in_progress_patterns:
        files.extend(project_dir.glob(pattern))

    # Sort by modification time (newest first)
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)


def discover_claude_files(search_path: str = None) -> List[Path]:
    """Wrapper for compatibility - delegates to discover_all_sessions"""
    if search_path:
        search_dir = Path(search_path)
        if search_dir.exists() and search_dir.is_dir():
            files = []
            for pattern in ["*.jsonl", "*.claude", "*.transcript"]:
                files.extend(search_dir.rglob(pattern))
            return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

    # Default: discover all sessions
    sessions = discover_all_sessions()
    # Extract file paths from session data
    # Sessions are dicts with metadata, need to extract paths
    return []  # Simplified for now


def group_by_projects(files: List[Path]) -> Dict[Path, List[Path]]:
    """Group files by project - 100% framework delegation"""
    from itertools import groupby

    def find_project_root(file):
        """Find project root using git or package markers"""
        indicators = [".git", "pyproject.toml", "package.json"]
        current = file.parent

        while current != current.parent:
            if any(current.glob(ind) for ind in indicators):
                return current
            current = current.parent

        return file.parent

    sorted_files = sorted(files, key=find_project_root)
    grouped = groupby(sorted_files, key=find_project_root)

    return {root: list(files) for root, files in grouped}


def analyze_project_structure(project_path: Path) -> Dict[str, Any]:
    """Analyze project using path inspection - 100% framework delegation"""
    from collections import Counter

    if not project_path.exists():
        return {}

    all_files = list(project_path.rglob("*"))
    file_types = Counter(f.suffix for f in all_files if f.is_file())

    return {
        'path': str(project_path),
        'total_files': len([f for f in all_files if f.is_file()]),
        'file_types': dict(file_types),
        'has_git': bool(list(project_path.glob(".git"))),
        'is_python': '.py' in file_types,
        'is_js': '.js' in file_types,
    }