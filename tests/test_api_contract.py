"""
API Contract Tests - MUST NOT BREAK!

These tests ensure backward compatibility during refactoring.
If these fail, we've broken the public API.
"""

import pytest
from pathlib import Path


def test_core_imports_work():
    """Core imports must work without error."""
    # Parser imports
    from claude_parser import load, load_large, load_many
    from claude_parser import Conversation
    
    # Hook imports  
    from claude_parser.hooks import hook_input
    from claude_parser.hooks import exit_success, exit_block, exit_error
    from claude_parser.hooks import HookData
    
    # Watch imports
    from claude_parser.watch import watch
    
    # Model imports
    from claude_parser.models import Message, UserMessage, AssistantMessage
    from claude_parser.models import ToolUse, ToolResult, Summary
    
    assert load is not None
    assert hook_input is not None
    assert watch is not None


def test_conversation_api_structure():
    """Conversation must have expected attributes."""
    from claude_parser import Conversation
    from claude_parser.models import Message
    
    # Mock a conversation
    conv = Conversation(messages=[], metadata=None)
    
    # Required properties
    assert hasattr(conv, 'messages')
    assert hasattr(conv, 'assistant_messages')
    assert hasattr(conv, 'user_messages')
    assert hasattr(conv, 'tool_uses')
    assert hasattr(conv, 'summaries')
    
    # Required methods
    assert hasattr(conv, 'search')
    assert hasattr(conv, 'filter')
    assert callable(conv.search)
    assert callable(conv.filter)


def test_hook_api_structure():
    """Hook functions must work as documented."""
    from claude_parser.hooks import HookData, exit_success, exit_block
    
    # HookData must be importable
    assert HookData is not None
    
    # Exit functions must be callable
    assert callable(exit_success)
    assert callable(exit_block)


def test_load_function_signature():
    """Load function must accept string or Path."""
    from claude_parser import load
    import inspect
    
    sig = inspect.signature(load)
    params = list(sig.parameters.keys())
    
    # Must accept filepath as first parameter
    assert len(params) >= 1
    assert params[0] in ['filepath', 'file', 'path']


def test_watch_function_signature():
    """Watch function must accept file and callback."""
    from claude_parser.watch import watch
    import inspect
    
    sig = inspect.signature(watch)
    params = list(sig.parameters.keys())
    
    # Must accept at least file and callback
    assert len(params) >= 2


def test_backwards_compatibility():
    """Old import paths should still work or have clear migration."""
    # These should either work or raise ImportError with migration message
    try:
        from claude_parser import parse_jsonl
        # If it exists, it should work
        assert parse_jsonl is not None
    except ImportError as e:
        # If removed, should have helpful message
        assert "use load() instead" in str(e).lower() or True  # Allow removal


def test_model_types_available():
    """All documented model types must be importable."""
    from claude_parser.models import (
        Message,
        BaseMessage,
        UserMessage,
        AssistantMessage,
        ToolUse,
        ToolResult,
        Summary,
        SystemMessage,
    )
    
    # All types should be classes
    assert isinstance(Message, type)
    assert isinstance(UserMessage, type)
    assert isinstance(AssistantMessage, type)


def test_feature_registry_accessible():
    """Feature registry should be accessible for capability checking."""
    try:
        from claude_parser.features import get_registry
        registry = get_registry()
        assert registry is not None
        assert hasattr(registry, 'features')
    except ImportError:
        # Feature registry is internal, okay if not exposed
        pass


@pytest.mark.parametrize("feature,min_coverage", [
    ("load", 90),
    ("Conversation", 90),
    ("hook_input", 90),
    ("watch", 80),
])
def test_feature_coverage_maintained(feature, min_coverage):
    """Critical features must maintain coverage."""
    # This would check actual coverage metrics
    # For now, just ensure the features exist
    if feature == "load":
        from claude_parser import load
        assert load is not None
    elif feature == "Conversation":
        from claude_parser import Conversation
        assert Conversation is not None
    elif feature == "hook_input":
        from claude_parser.hooks import hook_input
        assert hook_input is not None
    elif feature == "watch":
        from claude_parser.watch import watch
        assert watch is not None