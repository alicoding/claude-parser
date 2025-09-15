#!/usr/bin/env python3
"""
Session Discovery - Find all Claude sessions
@COMPOSITION: Returns plain dicts
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from more_itertools import first
from .session import load_session


def discover_all_sessions() -> List[Dict[str, Any]]:
    """Discover all sessions as plain dicts"""
    claude_path = os.getenv("CLAUDE_PROJECTS_PATH", "~/.claude/projects")
    claude_projects = Path(claude_path).expanduser()
    if not claude_projects.exists():
        return []
    
    # 100% pathlib + more-itertools: Get all project directories
    project_dirs = [d for d in claude_projects.iterdir() if d.is_dir()]
    
    # 100% framework delegation: Use map + filter instead of manual loops
    def load_newest_from_project(project_dir):
        jsonl_files = sorted((f for f in project_dir.glob("*.jsonl") if f.is_file()), 
                           key=lambda f: f.stat().st_mtime, reverse=True)
        if jsonl_files:
            return load_session(str(first(jsonl_files)))
        return None
    
    return list(filter(None, map(load_newest_from_project, project_dirs)))