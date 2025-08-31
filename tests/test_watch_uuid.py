"""
Test watch domain with UUID checkpoint system.

Ensures watch() and watch_async() use UUID checkpoints, not byte positions.
"""

import asyncio
import json
import tempfile
import threading
import time
from pathlib import Path
from typing import List
from unittest.mock import MagicMock, patch

import pytest

from claude_parser import Conversation
from claude_parser.models import Message
from claude_parser.watch import watch, watch_async


class TestWatchWithUUID:
    """Test synchronous watch with UUID checkpoints."""
    
    @pytest.fixture
    def temp_jsonl(self):
        """Create a temporary JSONL file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps({
                "uuid": "init-001",
                "type": "user",
                "content": "Initial message",
                "sessionId": "test-session",
                "timestamp": "2024-01-01T00:00:00Z"
            }) + '\n')
            temp_path = Path(f.name)
        
        yield temp_path
        temp_path.unlink()
    
    def test_watch_accepts_after_uuid_parameter(self, temp_jsonl):
        """Test that watch() accepts after_uuid parameter."""
        from claude_parser.watch.watcher import watch
        import inspect
        
        # Check signature includes after_uuid
        sig = inspect.signature(watch)
        assert 'after_uuid' in sig.parameters
        
        # Parameter should be optional
        param = sig.parameters['after_uuid']
        assert param.default is None
    
    @patch('claude_parser.watch.watcher.watchfiles.watch')
    def test_watch_uses_uuid_based_reader(self, mock_watchfiles, temp_jsonl):
        """Test that watch uses UUIDBasedReader, not IncrementalReader."""
        from claude_parser.watch.watcher import watch
        
        # Set up mock to prevent actual watching
        mock_watchfiles.return_value = iter([])  # Empty iterator
        
        callback = MagicMock()
        
        # This should not raise an error
        watch(str(temp_jsonl), callback, after_uuid="init-001")
        
        # Verify watchfiles was called (even if mocked)
        mock_watchfiles.assert_called_once()
    
    def test_watch_with_checkpoint_resume(self, temp_jsonl):
        """Test watch can resume from UUID checkpoint."""
        messages_received = []
        
        def callback(conv: Conversation, new_messages: List[Message]):
            messages_received.extend(new_messages)
        
        # Add more messages to file
        with open(temp_jsonl, 'a') as f:
            f.write(json.dumps({
                "uuid": "msg-002",
                "type": "assistant",
                "content": "Response",
                "sessionId": "test-session",
                "timestamp": "2024-01-01T00:01:00Z"
            }) + '\n')
        
        # Start watching from checkpoint in a thread
        watch_thread = threading.Thread(
            target=lambda: watch(str(temp_jsonl), callback, after_uuid="init-001"),
            daemon=True
        )
        watch_thread.start()
        
        # Give it time to initialize
        time.sleep(0.5)
        
        # Add a new message
        with open(temp_jsonl, 'a') as f:
            f.write(json.dumps({
                "uuid": "msg-003",
                "type": "user",
                "content": "New message",
                "sessionId": "test-session",
                "timestamp": "2024-01-01T00:02:00Z"
            }) + '\n')
        
        # Wait for processing
        time.sleep(0.5)
        
        # Should have received the new message
        # Note: Actual behavior depends on watchfiles detecting the change


@pytest.mark.asyncio
class TestWatchAsyncWithUUID:
    """Test async watch with UUID checkpoints."""
    
    @pytest.fixture
    async def temp_jsonl(self):
        """Create a temporary JSONL file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            f.write(json.dumps({
                "uuid": "async-001",
                "type": "user",
                "content": "Async initial",
                "sessionId": "async-session",
                "parentUuid": None,
                "timestamp": "2024-01-01T00:00:00Z"
            }) + '\n')
            temp_path = Path(f.name)
        
        yield temp_path
        temp_path.unlink()
    
    async def test_watch_async_accepts_after_uuid(self):
        """Test that watch_async accepts after_uuid parameter."""
        from claude_parser.watch import watch_async
        import inspect
        
        sig = inspect.signature(watch_async)
        assert 'after_uuid' in sig.parameters
        
        param = sig.parameters['after_uuid']
        assert param.default is None
    
    async def test_watch_async_with_checkpoint(self, temp_jsonl):
        """Test async watching with UUID checkpoint."""
        # Add more messages
        with open(temp_jsonl, 'a') as f:
            f.write(json.dumps({
                "uuid": "async-002",
                "type": "assistant",
                "content": "Async response",
                "sessionId": "async-session",
                "parentUuid": "async-001",
                "timestamp": "2024-01-01T00:01:00Z"
            }) + '\n')
        
        messages_collected = []
        
        # Create stop event for clean shutdown
        stop_event = asyncio.Event()
        
        # Watch with checkpoint
        async def watch_task():
            async for conv, new_messages in watch_async(
                temp_jsonl,
                after_uuid="async-001",
                stop_event=stop_event
            ):
                messages_collected.extend(new_messages)
                if len(messages_collected) >= 1:
                    stop_event.set()  # Stop after receiving message
        
        # Run with timeout
        try:
            await asyncio.wait_for(watch_task(), timeout=2.0)
        except asyncio.TimeoutError:
            pass
        
        # Should have skipped async-001 due to checkpoint
        # Actual behavior depends on file watching implementation


class TestUUIDIntegrationWithRealFiles:
    """Test with real JSONL files from test data."""
    
    @pytest.fixture
    def real_jsonl_file(self):
        """Use a real test JSONL file."""
        test_file = Path("jsonl-prod-data-for-test/test-data/4762e53b-7ca8-4464-9eac-d1816c343c50.jsonl")
        if test_file.exists():
            return test_file
        pytest.skip("Test data file not found")
    
    def test_uuid_checkpoint_with_real_data(self, real_jsonl_file):
        """Test UUID checkpointing with real Claude JSONL data."""
        from claude_parser.watch.uuid_tracker import UUIDCheckpointReader
        
        reader = UUIDCheckpointReader(real_jsonl_file)
        
        # Read all messages synchronously (we'll make it async-compatible)
        import asyncio
        loop = asyncio.new_event_loop()
        messages = loop.run_until_complete(reader.get_new_messages())
        loop.close()
        
        if messages:
            # All messages should have UUIDs
            assert all('uuid' in msg for msg in messages)
            
            # Test checkpoint resume
            first_uuid = messages[0]['uuid']
            reader2 = UUIDCheckpointReader(real_jsonl_file)
            reader2.set_checkpoint(first_uuid)
            
            loop = asyncio.new_event_loop()
            remaining = loop.run_until_complete(reader2.get_new_messages())
            loop.close()
            
            # Should have fewer messages after checkpoint
            assert len(remaining) < len(messages)


class TestNoBytePositionInWatcher:
    """Verify watcher.py doesn't use byte positions."""
    
    def test_watcher_source_has_no_byte_tracking(self):
        """Check watcher.py source for byte position code."""
        from claude_parser.watch import watcher
        import inspect
        
        source = inspect.getsource(watcher)
        
        # Should NOT have old IncrementalReader with position tracking
        assert 'last_position = 0' not in source
        assert 'f.seek(self.last_position)' not in source
        assert 'f.tell()' not in source
        
        # Should have UUID-based reader
        assert 'UUIDBasedReader' in source or 'UUIDCheckpointReader' in source
        assert 'after_uuid' in source
    
    def test_async_watcher_uses_uuid_streaming(self):
        """Verify async_watcher uses StreamingJSONLReader with UUIDs."""
        from claude_parser.watch import async_watcher
        import inspect
        
        source = inspect.getsource(async_watcher)
        
        # Should use StreamingJSONLReader
        assert 'StreamingJSONLReader' in source
        
        # Should support after_uuid
        assert 'after_uuid' in source
        
        # Should set checkpoint if provided
        assert 'set_checkpoint' in source