"""
TDD Tests for async watch functionality.

Following 95/5 principle - test with real scenarios.
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json
from claude_parser.watch import watch_async
from claude_parser.models import MessageType


class TestAsyncWatch:
    """Test async watch following TDD principles."""
    
    @pytest.mark.asyncio
    async def test_watch_async_detects_new_messages(self, tmp_path):
        """Test that watch_async detects new messages added to file."""
        # Create test file
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Hello"}}\n')
        
        # Track received messages
        received = []
        
        async def collect_messages():
            """Collect messages from watch_async."""
            async for conv, new_messages in watch_async(test_file):
                received.extend(new_messages)
                if len(received) >= 2:
                    break
        
        # Start watching
        task = asyncio.create_task(collect_messages())
        
        # Wait a bit for watcher to start
        await asyncio.sleep(0.1)
        
        # Append new message
        with open(test_file, 'a') as f:
            f.write('{"type": "assistant", "timestamp": "2025-08-21T00:00:01Z", "sessionId": "test", "message": {"content": "Hi there!"}}\n')
        
        # Wait for detection
        await asyncio.wait_for(task, timeout=2.0)
        
        # Verify
        assert len(received) >= 2
        assert received[0].type == MessageType.USER
        assert received[1].type == MessageType.ASSISTANT
    
    @pytest.mark.asyncio
    async def test_watch_async_with_message_filter(self, tmp_path):
        """Test filtering by message type."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('')
        
        received = []
        
        async def collect_filtered():
            """Collect only assistant messages."""
            async for conv, new_messages in watch_async(
                test_file, 
                message_types=["assistant"]
            ):
                received.extend(new_messages)
                if len(received) >= 1:
                    break
        
        task = asyncio.create_task(collect_filtered())
        await asyncio.sleep(0.1)
        
        # Write mixed messages
        with open(test_file, 'a') as f:
            f.write('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Hello"}}\n')
            f.write('{"type": "assistant", "timestamp": "2025-08-21T00:00:01Z", "sessionId": "test", "message": {"content": "Hi"}}\n')
        
        await asyncio.wait_for(task, timeout=2.0)
        
        # Should only have assistant messages
        assert len(received) == 1
        assert received[0].type == MessageType.ASSISTANT
    
    @pytest.mark.asyncio
    async def test_watch_async_handles_file_rotation(self, tmp_path):
        """Test that watch_async handles file truncation/rotation."""
        test_file = tmp_path / "test.jsonl"
        
        # Initial content
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "First"}}\n')
        
        received = []
        
        async def collect_all():
            """Collect all messages."""
            async for conv, new_messages in watch_async(test_file):
                received.extend(new_messages)
                if len(received) >= 3:
                    break
        
        task = asyncio.create_task(collect_all())
        await asyncio.sleep(0.1)
        
        # Simulate rotation - truncate and write new
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:02Z", "sessionId": "test", "message": {"content": "After rotation"}}\n')
        
        # Add another message
        with open(test_file, 'a') as f:
            f.write('{"type": "assistant", "timestamp": "2025-08-21T00:00:03Z", "sessionId": "test", "message": {"content": "Response"}}\n')
        
        await asyncio.wait_for(task, timeout=2.0)
        
        # Should have messages from both before and after rotation
        assert len(received) >= 3
    
    @pytest.mark.asyncio
    async def test_watch_async_with_stop_event(self, tmp_path):
        """Test stopping watch_async with event."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Hello"}}\n')
        
        stop_event = asyncio.Event()
        received_count = 0
        
        async def watch_with_stop():
            """Watch with stop event."""
            nonlocal received_count
            async for conv, new_messages in watch_async(test_file, stop_event=stop_event):
                received_count += len(new_messages)
        
        task = asyncio.create_task(watch_with_stop())
        
        # Let it start
        await asyncio.sleep(0.1)
        
        # Stop it
        stop_event.set()
        
        # Should complete quickly
        await asyncio.wait_for(task, timeout=1.0)
        
        # Should have processed initial message
        assert received_count >= 1
    
    @pytest.mark.asyncio
    async def test_watch_async_waits_for_file_creation(self, tmp_path):
        """Test that watch_async waits if file doesn't exist initially."""
        test_file = tmp_path / "not_yet.jsonl"
        
        received = []
        
        async def watch_nonexistent():
            """Watch file that doesn't exist yet."""
            async for conv, new_messages in watch_async(test_file):
                received.extend(new_messages)
                if len(received) >= 1:
                    break
        
        task = asyncio.create_task(watch_nonexistent())
        
        # Wait a bit
        await asyncio.sleep(0.1)
        
        # Create file
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Created"}}\n')
        
        # Should detect it
        await asyncio.wait_for(task, timeout=2.0)
        
        assert len(received) == 1
        assert "Created" in received[0].text_content
    
    @pytest.mark.asyncio  
    async def test_watch_async_handles_malformed_json(self, tmp_path):
        """Test that malformed JSON doesn't crash watch_async."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Good"}}\n')
        
        received = []
        
        async def watch_with_errors():
            """Watch file with some bad lines."""
            async for conv, new_messages in watch_async(test_file):
                received.extend(new_messages)
                if len(received) >= 2:
                    break
        
        task = asyncio.create_task(watch_with_errors())
        await asyncio.sleep(0.1)
        
        # Add malformed and good lines
        with open(test_file, 'a') as f:
            f.write('MALFORMED JSON\n')
            f.write('{"type": "assistant", "timestamp": "2025-08-21T00:00:01Z", "sessionId": "test", "message": {"content": "Still works"}}\n')
        
        await asyncio.wait_for(task, timeout=2.0)
        
        # Should skip malformed and process good messages
        assert len(received) == 2
        assert received[1].type == MessageType.ASSISTANT


class TestAsyncWatchPerformance:
    """Performance tests for async watch."""
    
    @pytest.mark.asyncio
    async def test_watch_async_low_latency(self, tmp_path):
        """Test that changes are detected quickly (<100ms)."""
        import time
        
        test_file = tmp_path / "perf.jsonl"
        test_file.write_text('')
        
        detection_time = None
        
        async def measure_latency():
            """Measure detection latency."""
            nonlocal detection_time
            async for conv, new_messages in watch_async(test_file):
                detection_time = time.time()
                break
        
        task = asyncio.create_task(measure_latency())
        await asyncio.sleep(0.1)
        
        # Write and measure
        write_time = time.time()
        with open(test_file, 'a') as f:
            f.write('{"type": "user", "timestamp": "2025-08-21T00:00:00Z", "sessionId": "test", "message": {"content": "Test"}}\n')
        
        await asyncio.wait_for(task, timeout=1.0)
        
        # Should detect in < 200ms (allowing some buffer)
        latency = (detection_time - write_time) * 1000
        assert latency < 200, f"Detection took {latency}ms"
    
    @pytest.mark.asyncio
    async def test_watch_async_handles_large_file(self, tmp_path):
        """Test that watch_async handles large files efficiently."""
        test_file = tmp_path / "large.jsonl"
        
        # Create large file (1000 messages)
        with open(test_file, 'w') as f:
            for i in range(1000):
                f.write(f'{{"type": "user", "timestamp": "2025-08-21T00:00:{i:02d}Z", "sessionId": "test", "message": {{"content": "Message {i}"}}}}\n')
        
        received_new = []
        
        async def watch_large():
            """Watch large file for new messages."""
            async for conv, new_messages in watch_async(test_file):
                # Should only get NEW messages, not reload all
                received_new.extend(new_messages)
                if len(received_new) >= 1:
                    break
        
        task = asyncio.create_task(watch_large())
        await asyncio.sleep(0.1)
        
        # Add one more message
        with open(test_file, 'a') as f:
            f.write('{"type": "assistant", "timestamp": "2025-08-21T00:01:00Z", "sessionId": "test", "message": {"content": "New message"}}\n')
        
        await asyncio.wait_for(task, timeout=2.0)
        
        # Should only receive the new message, not all 1001
        assert len(received_new) == 1
        assert received_new[0].type == MessageType.ASSISTANT