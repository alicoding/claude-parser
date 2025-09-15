#!/usr/bin/env python3
"""
Claude Parser - LNCA Architecture
Published package - clean API, zero backward compatibility
"""

# LNCA Core API - 100% Framework Delegation
from .main import load_session, load_latest_session, discover_all_sessions
from .analytics import analyze_session, analyze_project_contexts, analyze_tool_usage  
from .discovery import discover_claude_files, group_by_projects, analyze_project_structure, discover_current_project_files
from .operations import restore_file_content, generate_file_diff, compare_files, backup_file
from .navigation import find_message_by_uuid, get_message_sequence, get_timeline_summary
from .tokens import count_tokens, analyze_token_usage, estimate_cost, token_status
from .tokens.context import calculate_context_window
from .tokens.billing import calculate_session_cost
from .session import SessionManager

# Version info
__version__ = "2.0.0"

# Message types for filtering
class MessageType:
    USER = "user"
    ASSISTANT = "assistant" 
    SYSTEM = "system"

# Published API functions
def load_many(*paths):
    """Load multiple JSONL files"""
    from pathlib import Path
    # 100% framework delegation: Use filter instead of manual loop + append
    sessions = list(filter(None, (
        load_session(str(Path(path).expanduser())) 
        for path in paths
    )))
    return sessions

def find_current_transcript():
    """Find current Claude transcript (alias for load_latest_session)"""
    return load_latest_session()

# Clean exports - API only
__all__ = [
    'load_session', 'load_latest_session', 'discover_all_sessions', 
    'analyze_session', 'analyze_project_contexts', 'analyze_tool_usage',
    'discover_claude_files', 'group_by_projects', 'analyze_project_structure', 'discover_current_project_files',
    'restore_file_content', 'generate_file_diff', 'compare_files', 'backup_file',
    'find_message_by_uuid', 'get_message_sequence', 'get_timeline_summary',
    'count_tokens', 'analyze_token_usage', 'estimate_cost', 'token_status',
    'calculate_context_window', 'calculate_session_cost',
    'load_many', 'find_current_transcript', 
    'MessageType', '__version__'
]