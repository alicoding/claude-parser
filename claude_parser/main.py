#!/usr/bin/env python3
"""
Claude Parser - LNCA Entry Point  
@COMPOSITION: Returns plain dicts, no god objects
@SINGLE_SOURCE_TRUTH: Just imports and re-exports
"""

# Session loading functions
from .loaders.session import load_session, load_latest_session
from .loaders.discovery import discover_all_sessions

# Analytics functions - clean domain delegation
from .analytics import analyze_session, analyze_project_contexts, analyze_tool_usage

# Make functions available at package level
__all__ = [
    'load_session',
    'load_latest_session', 
    'discover_all_sessions',
    'analyze_session',
    'analyze_project_contexts',
    'analyze_tool_usage'
]