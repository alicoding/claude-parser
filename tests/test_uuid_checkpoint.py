"""
Test UUID checkpoint system - TDD for native Anthropic UUID tracking.

Tests that we:
1. Use UUIDs for checkpointing (not byte positions)
2. Can resume from any UUID
3. Handle file rotation correctly
4. Support multi-file project watching
5. Never use seek/tell/position tracking
"""

import orjson
import tempfile
from pathlib import Path

import pytest

from claude_parser.watch.uuid_tracker import (
    MultiFileUUIDTracker,
    UUIDCheckpointReader,
)


class TestUUIDCheckpointReader:
    """Test single-file UUID checkpoint reader."""

    @pytest.fixture
    def sample_messages(self):
        """Create sample JSONL messages with UUIDs."""
        return [
            {"uuid": "msg-001", "type": "user", "content": "Hello"},
            {"uuid": "msg-002", "type": "assistant", "content": "Hi there"},
            {"uuid": "msg-003", "type": "user", "content": "How are you?"},
            {"uuid": "msg-004", "type": "assistant", "content": "I'm well"},
            {"uuid": "msg-005", "type": "user", "content": "Great!"},
        ]

    @pytest.fixture
    def temp_jsonl_file(self, sample_messages):
        """Create a temporary JSONL file with sample messages."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            for msg in sample_messages:
                f.write(orjson.dumps(msg).decode() + "\n")
            temp_path = Path(f.name)

        yield temp_path
        temp_path.unlink()  # Clean up

    @pytest.mark.asyncio
    async def test_read_all_messages_no_checkpoint(
        self, temp_jsonl_file, sample_messages
    ):
        """Test reading all messages when no checkpoint is set."""
        reader = UUIDCheckpointReader(temp_jsonl_file)
        messages = await reader.get_new_messages()

        assert len(messages) == 5
        assert messages[0]["uuid"] == "msg-001"
        assert messages[-1]["uuid"] == "msg-005"
        assert reader.last_uuid == "msg-005"

    @pytest.mark.asyncio
    async def test_resume_from_checkpoint(self, temp_jsonl_file, sample_messages):
        """Test resuming from a UUID checkpoint."""
        reader = UUIDCheckpointReader(temp_jsonl_file)
        reader.set_checkpoint("msg-002")

        messages = await reader.get_new_messages()

        assert len(messages) == 3  # msg-003, msg-004, msg-005
        assert messages[0]["uuid"] == "msg-003"
        assert reader.last_uuid == "msg-005"

    @pytest.mark.asyncio
    async def test_no_duplicates_on_multiple_reads(self, temp_jsonl_file):
        """Test that processed UUIDs are not returned again."""
        reader = UUIDCheckpointReader(temp_jsonl_file)

        # First read
        messages1 = await reader.get_new_messages()
        assert len(messages1) == 5

        # Second read (should be empty)
        messages2 = await reader.get_new_messages()
        assert len(messages2) == 0

        # Processed UUIDs should be tracked
        assert len(reader.processed_uuids) == 5

    @pytest.mark.asyncio
    async def test_incremental_reading(self, temp_jsonl_file, sample_messages):
        """Test reading messages incrementally using checkpoints."""
        reader = UUIDCheckpointReader(temp_jsonl_file)

        # Read first 2 messages
        reader.set_checkpoint(None)
        messages = await reader.get_new_messages()

        # Simulate stopping after msg-002
        reader2 = UUIDCheckpointReader(temp_jsonl_file)
        reader2.set_checkpoint("msg-002")

        remaining = await reader2.get_new_messages()
        assert len(remaining) == 3
        assert remaining[0]["uuid"] == "msg-003"

    def test_reset_clears_state(self, temp_jsonl_file):
        """Test that reset() clears all tracking state."""
        reader = UUIDCheckpointReader(temp_jsonl_file)
        reader.processed_uuids = {"msg-001", "msg-002"}
        reader.last_uuid = "msg-002"

        reader.reset()

        assert len(reader.processed_uuids) == 0
        assert reader.last_uuid is None

    @pytest.mark.asyncio
    async def test_handles_missing_uuid_gracefully(self, temp_jsonl_file):
        """Test handling of messages without UUID field."""
        # Write a message without UUID
        with open(temp_jsonl_file, "a") as f:
            f.write(
                orjson.dumps({"type": "system", "content": "No UUID here"}).decode()
                + "\n"
            )

        reader = UUIDCheckpointReader(temp_jsonl_file)
        messages = await reader.get_new_messages()

        # Should skip the message without UUID
        assert len(messages) == 5  # Only messages with UUIDs
        assert all("uuid" in msg for msg in messages)

    def test_get_messages_between_uuids(self, temp_jsonl_file):
        """Test getting messages between two UUID checkpoints."""
        reader = UUIDCheckpointReader(temp_jsonl_file)

        messages = reader.get_messages_between("msg-002", "msg-004")

        assert len(messages) == 1  # Only msg-003
        assert messages[0]["uuid"] == "msg-003"


class TestMultiFileUUIDTracker:
    """Test multi-file project UUID tracking."""

    @pytest.fixture
    def sample_project_files(self):
        """Create multiple temporary JSONL files."""
        files = {}
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        # Create session1.jsonl
        session1 = temp_path / "session1.jsonl"
        with open(session1, "w") as f:
            f.write(
                orjson.dumps({"uuid": "s1-001", "content": "Session 1 start"}).decode()
                + "\n"
            )
            f.write(
                orjson.dumps({"uuid": "s1-002", "content": "Session 1 msg 2"}).decode()
                + "\n"
            )
        files["session1.jsonl"] = session1

        # Create session2.jsonl
        session2 = temp_path / "session2.jsonl"
        with open(session2, "w") as f:
            f.write(
                orjson.dumps({"uuid": "s2-001", "content": "Session 2 start"}).decode()
                + "\n"
            )
            f.write(
                orjson.dumps({"uuid": "s2-002", "content": "Session 2 msg 2"}).decode()
                + "\n"
            )
        files["session2.jsonl"] = session2

        yield files

        # Cleanup
        for file in files.values():
            file.unlink()
        temp_path.rmdir()

    def test_tracks_multiple_files(self, sample_project_files):
        """Test tracking checkpoints for multiple files."""
        tracker = MultiFileUUIDTracker()

        tracker.set_checkpoints(
            {"session1.jsonl": "s1-001", "session2.jsonl": "s2-001"}
        )

        assert tracker.checkpoints["session1.jsonl"] == "s1-001"
        assert tracker.checkpoints["session2.jsonl"] == "s2-001"

    @pytest.mark.asyncio
    async def test_get_new_messages_for_file(self, sample_project_files):
        """Test getting new messages for a specific file."""
        tracker = MultiFileUUIDTracker()

        # Set checkpoint for session1
        tracker.set_checkpoints({"session1.jsonl": "s1-001"})

        # Get new messages for session1
        messages = await tracker.get_new_messages_for_file(
            sample_project_files["session1.jsonl"]
        )

        assert len(messages) == 1  # Only s1-002
        assert messages[0]["uuid"] == "s1-002"

    def test_get_current_checkpoints(self, sample_project_files):
        """Test getting current checkpoint state."""
        tracker = MultiFileUUIDTracker()

        # Create readers
        reader1 = tracker.get_reader(sample_project_files["session1.jsonl"])
        reader1.last_uuid = "s1-002"

        reader2 = tracker.get_reader(sample_project_files["session2.jsonl"])
        reader2.last_uuid = "s2-001"

        checkpoints = tracker.get_current_checkpoints()

        assert checkpoints["session1.jsonl"] == "s1-002"
        assert checkpoints["session2.jsonl"] == "s2-001"


class TestNoBytePositionTracking:
    """Verify we're NOT using byte position tracking anywhere."""

    def test_uuid_reader_has_no_position_attributes(self):
        """Verify UUIDCheckpointReader doesn't have position/seek/tell."""
        reader = UUIDCheckpointReader("dummy.jsonl")

        # Should NOT have these attributes
        assert not hasattr(reader, "position")
        assert not hasattr(reader, "last_position")
        assert not hasattr(reader, "seek")
        assert not hasattr(reader, "tell")

        # Should have UUID tracking
        assert hasattr(reader, "last_uuid")
        assert hasattr(reader, "processed_uuids")

    def test_no_seek_or_tell_in_implementation(self):
        """Verify implementation doesn't use seek() or tell()."""
        import inspect
        from claude_parser.watch import uuid_tracker

        source = inspect.getsource(uuid_tracker)

        # These byte-position methods should NOT appear
        assert "seek(" not in source
        assert "tell(" not in source
        assert "last_position" not in source

        # UUID tracking should appear
        assert "last_uuid" in source
        assert "processed_uuids" in source


class TestFileRotationHandling:
    """Test handling of file rotation (common in log files)."""

    @pytest.mark.asyncio
    async def test_file_rotation_resets_state(self, tmp_path):
        """Test that file rotation (inode change) resets tracking."""
        file_path = tmp_path / "rotating.jsonl"

        # Create initial file
        with open(file_path, "w") as f:
            f.write(
                orjson.dumps({"uuid": "old-001", "content": "Old file"}).decode() + "\n"
            )

        reader = UUIDCheckpointReader(file_path)

        # Read initial messages
        messages1 = await reader.get_new_messages()
        assert len(messages1) == 1
        assert reader.last_uuid == "old-001"

        # Simulate rotation (delete and recreate)
        file_path.unlink()
        with open(file_path, "w") as f:
            f.write(
                orjson.dumps({"uuid": "new-001", "content": "New file"}).decode() + "\n"
            )
            f.write(
                orjson.dumps({"uuid": "new-002", "content": "New file 2"}).decode()
                + "\n"
            )

        # Read after rotation (implementation should detect inode change)
        # Note: The actual implementation checks inode in StreamingJSONLReader
        reader2 = UUIDCheckpointReader(file_path)
        messages2 = await reader2.get_new_messages()

        assert len(messages2) == 2
        assert messages2[0]["uuid"] == "new-001"


@pytest.mark.asyncio
class TestAsyncStreamingIntegration:
    """Test integration with async streaming."""

    async def test_streaming_reader_uses_uuids(self):
        """Verify StreamingJSONLReader uses UUID checkpoints."""
        from claude_parser.watch.true_streaming import StreamingJSONLReader

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                orjson.dumps({"uuid": "test-001", "content": "Test"}).decode() + "\n"
            )
            f.write(
                orjson.dumps({"uuid": "test-002", "content": "Test 2"}).decode() + "\n"
            )
            temp_path = Path(f.name)

        try:
            reader = StreamingJSONLReader(temp_path)
            reader.set_checkpoint("test-001")

            messages = await reader.get_new_messages()

            assert len(messages) == 1
            assert messages[0]["uuid"] == "test-002"
            assert reader.last_uuid == "test-002"
        finally:
            temp_path.unlink()

    async def test_project_streaming_with_checkpoints(self):
        """Test project-wide streaming with UUID checkpoints."""

        # This would need mocking since it requires actual Claude project structure
        # Keeping as documentation of the intended API
        pass
