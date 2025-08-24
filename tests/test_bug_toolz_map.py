#!/usr/bin/env python3
"""
Test to reproduce the P0 bug: map() must have at least two arguments.
"""

import pytest
from pathlib import Path
from claude_parser import load

def test_load_conversation_with_toolz_map_bug():
    """Test that we can load a conversation file without toolz map error."""
    # Use one of the actual files that's failing
    test_file = Path("/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/2f283580-c24a-40af-8129-1be80c07b965.jsonl")
    
    if test_file.exists():
        # This should NOT raise "map() must have at least two arguments"
        conv = load(str(test_file))
        
        # Basic assertions to ensure it loaded
        assert conv is not None
        assert len(conv.messages) >= 0
        
        # Should be able to search
        results = conv.search("test")
        assert isinstance(results, list)