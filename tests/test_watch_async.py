"""
Tests for async watch functionality using mocks.

Following the principle: test OUR code, not watchfiles library.
"""

import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path

import pytest

from claude_parser.models import MessageType
from claude_parser.watch import watch_async


class TestAsyncWatch:
    """Test async watch by mocking watchfiles - tests OUR processing logic."""

    @pytest.mark.asyncio
    async def test_watch_async_processes_changes(self, tmp_path):
        """Test that our code correctly processes file changes from watchfiles."""
        test_file = tmp_path / "test.jsonl"

        # Write both messages initially
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "Hello"}}\n'
            '{"type": "assistant", "uuid": "a1", "timestamp": "2025-08-21T00:00:01Z", "session_id": "test", "message": {"content": "Hi"}}\n'
        )

        # Mock watchfiles.awatch to emit one event
        async def mock_awatch(path, **kwargs):
            yield {("added", str(test_file))}

        all_messages = []

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file):
                all_messages.extend(new_messages)
                break  # Just process once

        # Verify our code processed both message types
        assert len(all_messages) == 2
        assert all_messages[0].type == MessageType.USER
        assert all_messages[1].type == MessageType.ASSISTANT

    @pytest.mark.asyncio
    async def test_watch_async_with_message_filter(self, tmp_path):
        """Test that message filtering works correctly."""
        test_file = tmp_path / "test.jsonl"

        # Create file with mixed message types
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "User msg"}}\n'
            '{"type": "assistant", "uuid": "a1", "timestamp": "2025-08-21T00:00:01Z", "session_id": "test", "message": {"content": "Assistant msg"}}\n'
            '{"type": "tool", "uuid": "t1", "timestamp": "2025-08-21T00:00:02Z", "session_id": "test", "tool": {"name": "Bash"}}\n'
        )

        # Mock watchfiles to return one event
        async def mock_awatch(path, **kwargs):
            yield {("added", str(test_file))}

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            # Test filtering for assistant messages only
            async for conv, new_messages in watch_async(
                test_file,
                message_types=["assistant"]
            ):
                # Should only get assistant messages
                assert all(msg.type == MessageType.ASSISTANT for msg in new_messages)
                assert len(new_messages) == 1
                assert new_messages[0].content == "Assistant msg"
                break

    @pytest.mark.asyncio
    async def test_watch_async_handles_malformed_json(self, tmp_path):
        """Test that malformed JSON is handled gracefully."""
        test_file = tmp_path / "test.jsonl"

        # Create file with some malformed lines
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "Valid"}}\n'
            'INVALID JSON LINE\n'
            '{"broken": json\n'
            '{"type": "assistant", "uuid": "a1", "timestamp": "2025-08-21T00:00:01Z", "session_id": "test", "message": {"content": "Also valid"}}\n'
        )

        # Mock watchfiles
        async def mock_awatch(path, **kwargs):
            yield {("added", str(test_file))}

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file):
                # Should skip malformed lines and only return valid messages
                assert len(new_messages) == 2
                assert new_messages[0].type == MessageType.USER
                assert new_messages[1].type == MessageType.ASSISTANT
                break

    @pytest.mark.asyncio
    async def test_watch_async_with_uuid_checkpoint(self, tmp_path):
        """Test resuming from UUID checkpoint."""
        test_file = tmp_path / "test.jsonl"

        # Create file with multiple messages
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "First"}}\n'
            '{"type": "assistant", "uuid": "a1", "timestamp": "2025-08-21T00:00:01Z", "session_id": "test", "message": {"content": "Second"}}\n'
            '{"type": "user", "uuid": "u2", "timestamp": "2025-08-21T00:00:02Z", "session_id": "test", "message": {"content": "Third"}}\n'
        )

        # Mock watchfiles
        async def mock_awatch(path, **kwargs):
            yield {("added", str(test_file))}

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            # Watch with checkpoint - should only get messages after "a1"
            async for conv, new_messages in watch_async(test_file, after_uuid="a1"):
                # Should only get the message after checkpoint
                assert len(new_messages) == 1
                assert new_messages[0].uuid == "u2"
                assert new_messages[0].content == "Third"
                break

    @pytest.mark.asyncio
    async def test_watch_async_stop_event(self, tmp_path):
        """Test that stop event works correctly."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "Test"}}\n'
        )

        stop_event = asyncio.Event()
        iterations = 0

        # Mock watchfiles to yield a few events then stop
        async def mock_awatch(path, stop_event=None, **kwargs):
            for i in range(3):  # Only yield 3 events max
                if stop_event and stop_event.is_set():
                    break
                yield {("modified", str(test_file))}
                await asyncio.sleep(0.01)

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file, stop_event=stop_event):
                iterations += 1
                if iterations >= 2:
                    stop_event.set()  # Stop after 2 iterations
                    break

        assert iterations >= 1  # Should have processed at least once


class TestAsyncWatchPerformance:
    """Performance tests for async watch."""

    @pytest.mark.asyncio
    async def test_watch_async_handles_large_file(self, tmp_path):
        """Test that large files are handled efficiently."""
        test_file = tmp_path / "large.jsonl"

        # Create a large file
        with open(test_file, "w") as f:
            for i in range(1000):
                f.write(f'{{"type": "user", "uuid": "u{i}", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {{"content": "Message {i}"}}}}\n')

        # Mock watchfiles
        async def mock_awatch(path, **kwargs):
            yield {("added", str(test_file))}

        message_count = 0

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file):
                message_count = len(new_messages)
                break

        # Should handle all messages
        assert message_count == 1000

    @pytest.mark.asyncio
    async def test_watch_async_low_latency(self, tmp_path):
        """Test that changes are detected with low latency."""
        test_file = tmp_path / "test.jsonl"
        test_file.write_text(
            '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "Test"}}\n'
        )

        # Mock watchfiles to emit events quickly
        async def mock_awatch(path, **kwargs):
            for i in range(3):
                yield {("modified", str(test_file))}
                await asyncio.sleep(0.01)  # Very short delay

        start_time = asyncio.get_event_loop().time()
        events_received = 0

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file):
                events_received += 1
                if events_received >= 3:
                    break

        elapsed = asyncio.get_event_loop().time() - start_time

        # Should process events quickly
        assert events_received >= 1  # At least one event processed
        assert elapsed < 1.0  # Should be fast

    @pytest.mark.asyncio
    async def test_watch_async_waits_for_file_creation(self, tmp_path):
        """Test waiting for file to be created."""
        test_file = tmp_path / "not_yet.jsonl"

        # Mock watchfiles to simulate file creation
        async def mock_awatch(path, **kwargs):
            # First, file doesn't exist
            await asyncio.sleep(0.1)
            # Create the file
            test_file.write_text(
                '{"type": "user", "uuid": "u1", "timestamp": "2025-08-21T00:00:00Z", "session_id": "test", "message": {"content": "Created"}}\n'
            )
            yield {("added", str(test_file))}

        with patch("claude_parser.watch.async_watcher.awatch", mock_awatch):
            async for conv, new_messages in watch_async(test_file):
                # Should get message once file is created
                assert len(new_messages) == 1
                assert new_messages[0].content == "Created"
                break
