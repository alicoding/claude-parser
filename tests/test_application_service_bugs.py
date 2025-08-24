"""
TDD tests to prove bugs found in conversation_service.py during code review.

These tests should FAIL initially, then pass after fixing the bugs.
"""

import pytest
from pathlib import Path
from claude_parser.application.conversation_service import ConversationService, load_large


class TestConversationServiceBugs:
    """Test bugs found during code review."""
    
    def test_get_repository_errors_attribute_bug(self):
        """
        BUG: get_repository_errors() references self._repository but constructor sets self.repository
        This should fail with AttributeError before fix.
        """
        service = ConversationService()
        
        # This should work, not raise AttributeError
        errors = service.get_repository_errors()
        assert isinstance(errors, list)
    
    def test_load_large_missing_method_bug(self):
        """
        BUG: load_large() calls service.load_conversation_streaming() which doesn't exist
        This should fail with AttributeError before fix.
        """
        # Create a test file (empty is fine for this test)
        test_file = Path("test_large.jsonl")
        test_file.write_text('{"type": "user", "content": "test"}\n')
        
        try:
            # This should work, not raise AttributeError for missing method
            conv = load_large(test_file)
            assert conv is not None
        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
    
    def test_factory_function_service_creation_inefficiency(self):
        """
        DESIGN ISSUE: Factory functions create new service instances every time
        This is inefficient - should reuse service instances.
        """
        from claude_parser.application.conversation_service import load, analyze
        
        # Create test file
        test_file = Path("test_conv.jsonl")
        test_file.write_text('{"type": "user", "content": "test"}\n')
        
        try:
            conv = load(test_file)
            
            # This should work without creating multiple service instances
            # (We can't easily test the instance reuse without refactoring, but the API should work)
            analysis = analyze(conv)
            assert isinstance(analysis, dict)
        finally:
            if test_file.exists():
                test_file.unlink()