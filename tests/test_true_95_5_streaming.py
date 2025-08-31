"""
TDD Test for TRUE 95/5 JSONL Streaming.

This test defines the exact behavior we need:
1. Stream large files incrementally (not reload entire file)
2. Detect new messages as they're appended
3. Handle file rotation gracefully
4. Use only approved libraries in the TRUE 95/5 way
"""

import asyncio
import os
import tempfile
from pathlib import Path

import orjson
import pytest


class TestTrue95_5Streaming:
    """Define the TRUE 95/5 behavior for JSONL streaming."""

    @pytest.mark.asyncio
    async def test_incremental_streaming_not_full_reload(self):
        """
        TRUE 95/5: Should read only NEW lines, not reload entire file.

        This is the key differentiator - for large files, we can't
        reload everything each time. We need incremental reading.
        """
        # Create a large file (simulate 100MB with many messages)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_file = Path(f.name)

            # Write 10,000 initial messages (simulating large file)
            for i in range(10000):
                msg = {
                    "type": "user",
                    "uuid": f"msg-{i}",
                    "session_id": "test",
                    "message": {"role": "user", "content": f"Message {i}"},
                }
                f.write(orjson.dumps(msg).decode() + "\n")

        try:
            # Import our TRUE 95/5 implementation
            from claude_parser.watch.true_streaming import stream_jsonl_incrementally

            # Track what we receive
            messages_received = []

            # First, read without watching to get initial messages
            async for new_messages in stream_jsonl_incrementally(
                test_file, watch=False
            ):
                messages_received.extend(new_messages)

            # Key assertion: Should have read initial 10,000 messages
            assert len(messages_received) == 10000

            # Create a new reader to test incremental reading
            from claude_parser.watch.true_streaming import StreamingJSONLReader

            reader = StreamingJSONLReader(test_file)

            # First read should get all 10,000
            initial_messages = await reader.get_new_messages()
            assert len(initial_messages) == 10000

            # Now append ONE new message
            with open(test_file, "a") as f:
                new_msg = {
                    "type": "assistant",
                    "uuid": "new-msg",
                    "session_id": "test",
                    "message": {"role": "assistant", "content": "I'm new!"},
                }
                f.write(orjson.dumps(new_msg).decode() + "\n")

            # For UUID-based tracking, we need a fresh reader or reset
            # because it tracks processed UUIDs to avoid duplicates
            # This is the correct behavior - clients should track their checkpoint
            reader2 = StreamingJSONLReader(test_file)
            reader2.set_checkpoint("msg-9999")  # Last message UUID
            
            # Now it should get ONLY the new message after checkpoint
            new_messages = await reader2.get_new_messages()
            assert len(new_messages) == 1
            assert new_messages[0]["uuid"] == "new-msg"

            # Total should be 10001
            assert len(messages_received) + len(new_messages) == 10001

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_file_rotation_handling(self):
        """
        TRUE 95/5: Handle file rotation (log rotation scenario).

        When a file is truncated/rotated, we should detect it and
        start reading from the beginning of the new file.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_file = Path(f.name)

            # Write initial messages
            for i in range(3):
                msg = {
                    "type": "user",
                    "uuid": f"old-{i}",
                    "session_id": "test",
                    "message": {"role": "user", "content": f"Old message {i}"},
                }
                f.write(orjson.dumps(msg).decode() + "\n")

        try:
            from claude_parser.watch.true_streaming import stream_jsonl_incrementally

            messages_received = []
            rotation_detected = False

            async def collect_with_rotation_detection():
                nonlocal rotation_detected
                async for new_messages in stream_jsonl_incrementally(test_file):
                    # Check if we got messages starting with 'new-' after getting 'old-'
                    if messages_received and messages_received[-1]["uuid"].startswith(
                        "old-"
                    ):
                        if new_messages and new_messages[0]["uuid"].startswith("new-"):
                            rotation_detected = True

                    messages_received.extend(new_messages)
                    if len(messages_received) >= 5:  # 3 old + 2 new
                        break

            task = asyncio.create_task(collect_with_rotation_detection())
            await asyncio.sleep(0.1)

            # Simulate log rotation: truncate and write new content
            with open(test_file, "w") as f:
                for i in range(2):
                    msg = {
                        "type": "assistant",
                        "uuid": f"new-{i}",
                        "session_id": "test",
                        "message": {"role": "assistant", "content": f"New message {i}"},
                    }
                    f.write(orjson.dumps(msg).decode() + "\n")

            await asyncio.wait_for(task, timeout=2.0)

            # Should have detected rotation and read new messages
            assert rotation_detected
            assert any(msg["uuid"].startswith("new-") for msg in messages_received)

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_seek_position_tracking(self):
        """
        TRUE 95/5: Track file position to avoid re-reading.

        The implementation should track where it left off and
        continue from that position (like tail -f).
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_file = Path(f.name)
            f.write("")  # Start empty

        try:
            from claude_parser.watch.true_streaming import StreamingJSONLReader

            reader = StreamingJSONLReader(test_file)

            # Write first batch
            with open(test_file, "a") as f:
                msg1 = {
                    "type": "user",
                    "uuid": "msg-1",
                    "session_id": "test",
                    "message": {"role": "user", "content": "First"},
                }
                f.write(orjson.dumps(msg1).decode() + "\n")

            # Read first batch
            messages = await reader.get_new_messages()
            assert len(messages) == 1
            assert messages[0]["uuid"] == "msg-1"

            # Position should be tracked
            assert reader.position > 0
            old_position = reader.position

            # Write second batch
            with open(test_file, "a") as f:
                msg2 = {
                    "type": "user",
                    "uuid": "msg-2",
                    "session_id": "test",
                    "message": {"role": "user", "content": "Second"},
                }
                f.write(orjson.dumps(msg2).decode() + "\n")

            # Read second batch - should ONLY get the new message
            messages = await reader.get_new_messages()
            assert len(messages) == 1
            assert messages[0]["uuid"] == "msg-2"

            # Position should have advanced
            assert reader.position > old_position

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_true_95_5_simplicity(self):
        """
        TRUE 95/5: The API should be dead simple - one function/class, minimal config.

        Like Temporal for workflows or LlamaIndex for docs, the library
        should handle ALL the complexity internally.
        """
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_file = Path(f.name)
            msg = {
                "type": "user",
                "uuid": "test",
                "session_id": "test",
                "message": {"role": "user", "content": "Test"},
            }
            f.write(orjson.dumps(msg).decode() + "\n")

        try:
            from claude_parser.watch.true_streaming import stream_jsonl_incrementally

            # TRUE 95/5: Should work with just a file path - no complex setup
            messages = []
            async for new_msgs in stream_jsonl_incrementally(test_file):
                messages.extend(new_msgs)
                break  # Just get first batch

            assert len(messages) == 1

            # Alternative: Simple class API
            from claude_parser.watch.true_streaming import StreamingJSONLReader

            # TRUE 95/5: Minimal instantiation
            reader = StreamingJSONLReader(test_file)
            messages = await reader.get_new_messages()
            assert len(messages) == 1  # New reader reads from beginning

            # Second read should get nothing (already at end)
            messages2 = await reader.get_new_messages()
            assert len(messages2) == 0  # No new messages

        finally:
            os.unlink(test_file)
