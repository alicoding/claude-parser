#!/usr/bin/env python3
"""
Project Context Analytics
@COMPOSITION: Plain dict processing
"""

from typing import Dict, Any
from collections import Counter


def analyze_project_contexts(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze project contexts from session dict"""
    if not session_data:
        return {'projects': {}, 'contexts': []}
    
    messages = session_data.get('messages', [])
    if not messages:
        return {'projects': {}, 'contexts': []}
    
    # Use Counter for project context frequency
    project_counter = Counter()
    contexts_seen = set()
    
    for msg in messages:
        # Check for project context in various locations
        project_context = (msg.get('project_context') or 
                          msg.get('cwd') or
                          msg.get('project'))
        
        if project_context:
            project_counter[project_context] += 1
            contexts_seen.add(project_context)
    
    return {
        'projects': dict(project_counter),
        'contexts': list(contexts_seen),
        'total_contexts': sum(project_counter.values())
    }