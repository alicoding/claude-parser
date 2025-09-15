#!/usr/bin/env python3
"""
LNCA Test Configuration - Shared Fixtures
100% framework delegation - pytest + existing discovery components
@COMPOSITION: Works with plain dicts
"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_claude_jsonl():
    """Shared fixture for Claude JSONL test data - uses existing discovery"""
    from claude_parser import load_latest_session
    return load_latest_session()


@pytest.fixture
def session_factory():
    """Factory fixture for creating session dicts"""
    def _create_session(message_count=3, with_tools=False):
        messages = []
        raw_data = []
        
        for i in range(message_count):
            # Create message dict
            message = {
                'uuid': f"msg_{i}",
                'content': {"text": f"Test message {i}"},
                'type': "user" if i % 2 == 0 else "assistant",
            }
            
            if with_tools and i % 2 == 0:
                message['tool_use_id'] = f"tool_{i}"
                
            messages.append(message)
            
            # Create corresponding raw_data
            raw_data.append({
                'uuid': f"msg_{i}",
                'type': message['type'],
                'content': message['content']
            })
        
        return {
            'session_id': "test_session",
            'messages': messages,
            'metadata': {"total_tokens": message_count * 100},
            'raw_data': raw_data
        }
    
    return _create_session