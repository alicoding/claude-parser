#!/usr/bin/env python3
"""
Session Loading - Core loading functionality
@COMPOSITION: Returns plain dicts
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from more_itertools import first
from ..session import SessionManager


def load_session(identifier: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Load session as plain dict - @COMPOSITION pattern"""
    manager = SessionManager()
    
    if identifier:
        # Direct path provided
        path = Path(identifier)
        if not path.exists() or not path.is_file():
            return None
    else:
        # No path - use CWD encoding with framework delegation
        cwd = str(Path.cwd())
        encoded_path = cwd.replace('/', '-')
        claude_path = os.getenv("CLAUDE_PROJECTS_PATH", "~/.claude/projects")
        project_dir = Path(claude_path).expanduser() / encoded_path
        
        if not project_dir.exists():
            return None
            
        # 100% pathlib + more-itertools: Find newest JSONL file
        jsonl_files = sorted((f for f in project_dir.glob("*.jsonl") if f.is_file()), 
                           key=lambda f: f.stat().st_mtime, reverse=True)
        if not jsonl_files:
            return None
            
        path = first(jsonl_files)
    
    # Load and validate
    messages = manager.load_jsonl(str(path))
    if not messages:
        return None
        
    # Validate CWD matches (if no identifier provided)
    if not identifier and messages:
        first_msg = messages[0]
        if 'cwd' in first_msg and first_msg['cwd'] != str(Path.cwd()):
            return None  # CWD mismatch
    
    # Return plain dict - @COMPOSITION pattern
    return {
        'session_id': path.stem,
        'messages': messages,  # Already plain dicts from manager
        'metadata': {'transcript_path': str(path)},
        'raw_data': messages
    }


def load_latest_session() -> Optional[Dict[str, Any]]:
    """Load most recent Claude session as dict"""
    return load_session()