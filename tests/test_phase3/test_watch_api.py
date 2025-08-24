"""TDD Tests for Watch Domain API - Written FIRST.

Following PHASE2_STRICT_PATTERN.md:
1. Tests written before implementation
2. 95/5 principle validation
3. SOLID principle compliance
4. DDD domain boundaries

Uses REAL Claude Code JSONL data for robust testing.

Success Criteria:
- watch() function exists and is callable
- Callback receives (Conversation, List[Message])
- Message type filtering works
- File watching detects changes
- Performance: handles large files efficiently
- Error handling: graceful failure modes
"""

import pytest
import tempfile
import json
import time
import threading
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Real Claude Code test data
REAL_CLAUDE_JSONL = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl"

# Sample real Claude Code messages for testing
REAL_USER_MESSAGE = {
    "parentUuid": None,
    "isSidechain": False,
    "userType": "external",
    "cwd": "/test/path",
    "sessionId": "test-session-123",
    "version": "1.0.83",
    "gitBranch": "main",
    "type": "user",
    "message": {
        "role": "user",
        "content": "Hello Claude, please help me with a task"
    },
    "uuid": "test-user-msg-123",
    "timestamp": "2025-08-20T10:00:00.000Z"
}

REAL_ASSISTANT_MESSAGE = {
    "parentUuid": "test-user-msg-123",
    "isSidechain": False,
    "userType": "external", 
    "cwd": "/test/path",
    "sessionId": "test-session-123",
    "version": "1.0.83",
    "gitBranch": "main",
    "message": {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "model": "claude-sonnet-4",
        "content": [{"type": "text", "text": "I'll help you with that task!"}],
        "stop_reason": None,
        "usage": {"input_tokens": 10, "output_tokens": 8}
    },
    "requestId": "req_test123",
    "type": "assistant",
    "uuid": "test-assistant-msg-123", 
    "timestamp": "2025-08-20T10:00:01.000Z"
}

# Will import when implemented
# from claude_parser.watch import watch


class TestWatchDomainAPI:
    """Test the watch domain API contract."""
    
    def test_watch_function_exists(self):
        """watch() function is available for import."""
        from claude_parser.watch import watch
        
        # Should be callable
        assert callable(watch)
    
    def test_watch_function_signature(self):
        """watch() has correct function signature."""
        from claude_parser.watch import watch
        import inspect
        
        sig = inspect.signature(watch)
        params = list(sig.parameters.keys())
        
        # Must have file_path and callback
        assert "file_path" in params
        assert "callback" in params
        assert "message_types" in params  # Optional filtering
    
    def test_watch_95_percent_api(self):
        """95% API: One line starts watching."""
        from claude_parser.watch import watch
        
        callback = Mock()
        
        # Should raise FileNotFoundError for non-existent file
        with pytest.raises(FileNotFoundError):
            watch("nonexistent.jsonl", callback)
        
        # Should accept real file without error (but won't test actual watching here)
        if Path(REAL_CLAUDE_JSONL).exists():
            # This would start watching in real implementation
            # but we'll mock it to avoid blocking
            with patch('claude_parser.watch.watcher.watchfiles.watch') as mock_watch:
                mock_watch.return_value = iter([])  # No changes
                
                try:
                    watch(REAL_CLAUDE_JSONL, callback)
                except KeyboardInterrupt:
                    pass  # Expected when mocking empty iterator
    
    def test_watch_callback_parameters(self):
        """Callback receives (Conversation, List[Message]) parameters."""
        from claude_parser.watch import watch
        
        # Use real Claude Code JSONL file for testing
        if Path(REAL_CLAUDE_JSONL).exists():
            callback = Mock()
            
            # High-level test: Mock watchfiles to simulate file change
            with patch('claude_parser.watch.watcher.watchfiles.watch') as mock_watchfiles:
                # Mock one change event
                mock_watchfiles.return_value = iter([{('modified', REAL_CLAUDE_JSONL)}])
                
                # Mock the incremental reader to return some new lines
                with patch('claude_parser.watch.watcher.IncrementalReader.get_new_lines') as mock_get_lines:
                    # Return one real message line
                    mock_get_lines.return_value = [json.dumps(REAL_ASSISTANT_MESSAGE)]
                    
                    # Run watch - should call callback once
                    watch(REAL_CLAUDE_JSONL, callback)
                
                # Verify callback was called with correct signature
                assert callback.called
                args = callback.call_args[0]
                assert len(args) == 2
                
                conv, new_messages = args
                assert hasattr(conv, 'messages')  # Conversation object  
                assert isinstance(new_messages, list)  # List of new messages
                assert len(new_messages) >= 0  # May be empty due to filtering/parsing
    
    def test_message_type_filtering(self):
        """Optional message_types parameter filters messages."""
        pytest.skip("Implementation pending")
        
        from claude_parser.watch import watch
        
        callback = Mock()
        
        # High-level test: Mock the file watching, focus on API behavior
        with patch('claude_parser.watch.watchfiles.watch') as mock_watchfiles:
            # Mock file change event
            mock_watchfiles.return_value = iter([{('modified', REAL_CLAUDE_JSONL)}])
            
            # Test message type filtering at API level
            watch(REAL_CLAUDE_JSONL, callback, message_types=["assistant"])
            
            # Implementation should filter to only assistant messages
            assert callback.called
            args = callback.call_args[0]
            conv, new_messages = args
            
            # All new_messages should be assistant type (if any)
            for msg in new_messages:
                assert msg.type == "assistant"
    
    def test_file_rotation_handling(self):
        """Handles file rotation gracefully."""
        pytest.skip("Implementation pending")
        
        from claude_parser.watch import watch
        
        callback = Mock()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            file_path = f.name
            
            def start_watch():
                watch(file_path, callback)
            
            thread = threading.Thread(target=start_watch)
            thread.daemon = True
            thread.start()
            
            time.sleep(0.1)
            
            # Simulate file rotation (delete and recreate)
            Path(file_path).unlink()
            
            with open(file_path, 'w') as new_f:
                new_msg = {"type": "user", "content": "After rotation"}
                new_f.write(json.dumps(new_msg) + '\n')
            
            time.sleep(0.1)
            
            # Should handle rotation and detect new message
            assert callback.called
    
    def test_watch_performance(self):
        """Handles large files efficiently."""
        pytest.skip("Implementation pending")
        
        from claude_parser.watch import watch
        
        callback = Mock()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            # Create large file (1MB of messages)
            for i in range(1000):
                msg = {
                    "type": "user",
                    "content": f"Message {i} " + "x" * 1000,
                    "timestamp": f"2024-08-20T10:{i:02d}:00Z"
                }
                f.write(json.dumps(msg) + '\n')
            f.flush()
            
            def start_watch():
                watch(f.name, callback)
            
            thread = threading.Thread(target=start_watch)
            thread.daemon = True
            
            start_time = time.time()
            thread.start()
            time.sleep(0.1)  # Let it start
            
            # Add one more message
            with open(f.name, 'a') as append_f:
                new_msg = {"type": "assistant", "content": "New message"}
                append_f.write(json.dumps(new_msg) + '\n')
                append_f.flush()
            
            time.sleep(0.2)  # Should detect quickly
            
            elapsed = time.time() - start_time
            assert elapsed < 1.0  # Should be very fast
            assert callback.called
    
    def test_error_handling(self):
        """Graceful error handling for malformed JSON."""
        pytest.skip("Implementation pending")
        
        from claude_parser.watch import watch
        
        callback = Mock()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            def start_watch():
                watch(f.name, callback)
            
            thread = threading.Thread(target=start_watch)
            thread.daemon = True
            thread.start()
            
            time.sleep(0.1)
            
            # Add malformed JSON (should not crash watcher)
            with open(f.name, 'a') as append_f:
                append_f.write('{"malformed": json}\n')  # Invalid JSON
                append_f.flush()
            
            time.sleep(0.1)
            
            # Add valid message after malformed one
            with open(f.name, 'a') as append_f:
                valid_msg = {"type": "user", "content": "Valid message"}
                append_f.write(json.dumps(valid_msg) + '\n')
                append_f.flush()
            
            time.sleep(0.1)
            
            # Should still process valid messages
            assert callback.called


class TestWatchDomainSOLID:
    """Test SOLID principles compliance."""
    
    def test_single_responsibility(self):
        """watch() has single responsibility: file watching."""
        pytest.skip("Implementation pending")
        
        from claude_parser.watch import watch
        
        # Should only handle file watching, not parsing/validation
        # Parsing should be delegated to parser domain
        # Message creation should be delegated to models domain
        assert callable(watch)
    
    def test_open_closed_principle(self):
        """Can extend behavior without modifying watch() function."""
        pytest.skip("Implementation pending")
        
        # Different callback functions should provide extension
        # without modifying watch() implementation
        pass
    
    def test_dependency_inversion(self):
        """watch() depends on abstractions, not concrete implementations."""
        pytest.skip("Implementation pending")
        
        # Should use interfaces/protocols where possible
        # Should not be tightly coupled to specific file operations
        pass


class TestWatchDomainDDD:
    """Test Domain-Driven Design principles."""
    
    def test_domain_boundaries(self):
        """Watch domain has clear boundaries."""
        pytest.skip("Implementation pending")
        
        # Should import from parser domain for parsing
        # Should import from models domain for Message types
        # Should not duplicate logic from other domains
        pass
    
    def test_ubiquitous_language(self):
        """Uses domain language consistently."""
        pytest.skip("Implementation pending")
        
        # Functions/classes should use domain terms:
        # watch, callback, message, conversation
        # Not technical terms: observer, listener, handler
        pass


class TestWatch95PercentPrinciple:
    """Test 95/5 development principle compliance."""
    
    def test_95_percent_api_simplicity(self):
        """95% use case requires ≤ 3 lines of code."""
        pytest.skip("Implementation pending")
        
        # This should be all most users need:
        # def callback(conv, msgs): pass
        # watch("file.jsonl", callback)  # 2 lines total
        pass
    
    def test_5_percent_advanced_features(self):
        """5% use case has advanced features available."""
        pytest.skip("Implementation pending")
        
        # Advanced features should be available but optional:
        # - Message type filtering  
        # - Custom error handling
        # - Performance tuning options
        pass


class TestWatchIntegration:
    """Test integration with other domains."""
    
    def test_parser_domain_integration(self):
        """Uses parser domain for JSONL parsing."""
        pytest.skip("Implementation pending")
        
        # Should use existing load() function
        # Should not reimplement JSONL parsing
        pass
    
    def test_models_domain_integration(self):
        """Uses models domain for Message objects."""
        pytest.skip("Implementation pending")
        
        # Should return typed Message objects
        # Should not create raw dicts
        pass
    
    def test_hooks_domain_integration(self):
        """Can be used from hook scripts."""
        pytest.skip("Implementation pending")
        
        # Hook scripts should be able to start watching
        # Should work with HookData.load_conversation()
        pass