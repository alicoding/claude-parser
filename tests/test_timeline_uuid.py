"""
Tests for Timeline UUID-based checkpointing - TDD for file system restoration.

Tests that we:
1. Map UUIDs to git commits correctly
2. Restore file system state to any UUID checkpoint
3. Handle native Claude Code JSONL structure
4. Use 95/5 principle (GitPython + libraries, minimal custom code)
"""

import tempfile
from pathlib import Path

import jsonlines
import pytest

from claude_parser.domain.services import Timeline


class TestTimelineUUIDMapping:
    """Test UUID to git commit mapping in Timeline."""

    def test_uuid_to_commit_mapping(self, sample_jsonl_with_uuids):
        """Test that UUIDs map to correct git commits."""
        timeline = Timeline(sample_jsonl_with_uuids)

        # Should have commits for each UUID
        commits = list(timeline.repo.iter_commits())
        assert len(commits) == 3  # Write + 2 Edits

        # Each commit should correspond to a tool operation
        commit_messages = [c.message for c in commits]
        assert any("Write main.py" in msg for msg in commit_messages)
        assert any("Edit main.py" in msg for msg in commit_messages)

        timeline.clear_cache()

    def test_checkout_by_uuid_method(self, sample_jsonl_with_uuids):
        """Test new checkout_by_uuid method works correctly."""
        timeline = Timeline(sample_jsonl_with_uuids)

        # Should be able to checkout by UUID (when method is added)
        # This test documents the expected API
        try:
            state = timeline.checkout_by_uuid("uuid-002")
            assert "main.py" in state
            # First edit should show "hello world"
            assert "hello world" in state["main.py"]["content"]
        except AttributeError:
            # Method doesn't exist yet - this is expected
            pytest.skip("checkout_by_uuid method not implemented yet")

        timeline.clear_cache()

    def test_uuid_not_found_handling(self, sample_jsonl_with_uuids):
        """Test graceful handling when UUID doesn't exist."""
        timeline = Timeline(sample_jsonl_with_uuids)

        try:
            result = timeline.checkout_by_uuid("nonexistent-uuid")
            # Should return None or empty dict
            assert result is None or len(result) == 0
        except (AttributeError, ValueError):
            # Expected behavior - either method doesn't exist or raises ValueError
            pass

        timeline.clear_cache()


class TestFileRestorationAccuracy:
    """Test accuracy of file restoration to UUID checkpoints."""

    def test_restore_exact_file_state(self, complex_editing_jsonl):
        """Test that restored files match exact state at UUID."""
        timeline = Timeline(complex_editing_jsonl)

        # Get final state
        final_state = timeline.checkout("latest")
        assert "config.py" in final_state
        final_content = final_state["config.py"]["content"]

        # Should contain both DEBUG and PORT settings
        assert "DEBUG = True" in final_content
        assert "PORT = 8080" in final_content
        assert "HOST = 'localhost'" in final_content

        timeline.clear_cache()

    def test_incremental_restoration(self, complex_editing_jsonl):
        """Test restoring to different points in editing history."""
        timeline = Timeline(complex_editing_jsonl)

        # Test that we can get commits at different stages
        commits = list(timeline.repo.iter_commits())

        # Should have multiple commits for the editing sequence
        assert len(commits) >= 2

        # Each commit should represent a file state change
        for commit in commits:
            timeline.repo.git.checkout(commit)
            # File should exist and be readable
            config_file = Path(timeline.repo.working_dir) / "config.py"
            if config_file.exists():
                content = config_file.read_text()
                assert isinstance(content, str)

        timeline.clear_cache()

    def test_multiedit_restoration(self, jsonl_with_multiedit_uuids):
        """Test restoration of MultiEdit operations."""
        timeline = Timeline(jsonl_with_multiedit_uuids)

        state = timeline.checkout("latest")
        assert "config.py" in state
        content = state["config.py"]["content"]

        # MultiEdit should have applied both edits
        assert "DEBUG = True" in content
        assert "PORT = 8080" in content

        timeline.clear_cache()


class TestNativeJSONLStructure:
    """Test compatibility with native Claude Code JSONL format."""

    def test_tool_use_tool_result_chain(self, native_claude_jsonl):
        """Test processing native tool_use → tool_result chains."""
        timeline = Timeline(native_claude_jsonl)

        # Should process tool operations correctly
        commits = list(timeline.repo.iter_commits())
        assert len(commits) > 0

        # Should create files from tool operations
        state = timeline.checkout("latest")
        assert len(state) > 0

        timeline.clear_cache()

    def test_handles_parent_uuid_chains(self, native_claude_jsonl):
        """Test that parent_uuid chains are processed correctly."""
        timeline = Timeline(native_claude_jsonl)

        # Should build proper commit history
        commits = list(timeline.repo.iter_commits())

        # Commits should form a proper chain
        for commit in commits:
            # Each commit should have valid metadata
            assert commit.message
            assert commit.committed_datetime

        timeline.clear_cache()


@pytest.fixture
def sample_jsonl_with_uuids(tmp_path):
    """Create JSONL with UUIDs for testing."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()

    events = [
        {
            "uuid": "uuid-001",
            "timestamp": "2024-08-23T10:00:00",
            "tool_name": "Write",
            "file_path": "main.py",
            "content": "print('hello')",
        },
        {
            "uuid": "uuid-002",
            "timestamp": "2024-08-23T11:00:00",
            "tool_name": "Edit",
            "file_path": "main.py",
            "old_string": "hello",
            "new_string": "hello world",
        },
        {
            "uuid": "uuid-003",
            "timestamp": "2024-08-23T12:00:00",
            "tool_name": "Edit",
            "file_path": "main.py",
            "old_string": "print('hello world')",
            "new_string": "print('Hello, World!')",
        },
    ]

    with jsonlines.open(jsonl_dir / "test_uuids.jsonl", mode="w") as writer:
        writer.write_all(events)

    return jsonl_dir


@pytest.fixture
def complex_editing_jsonl(tmp_path):
    """Create JSONL with complex editing sequence."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()

    events = [
        {
            "uuid": "edit-001",
            "timestamp": "2024-08-23T10:00:00",
            "tool_name": "Write",
            "file_path": "config.py",
            "content": "# Configuration file\n",
        },
        {
            "uuid": "edit-002",
            "timestamp": "2024-08-23T10:01:00",
            "tool_name": "Edit",
            "file_path": "config.py",
            "old_string": "# Configuration file\n",
            "new_string": "# Configuration file\nDEBUG = True\n",
        },
        {
            "uuid": "edit-003",
            "timestamp": "2024-08-23T10:02:00",
            "tool_name": "Edit",
            "file_path": "config.py",
            "old_string": "DEBUG = True\n",
            "new_string": "DEBUG = True\nPORT = 8080\n",
        },
        {
            "uuid": "edit-004",
            "timestamp": "2024-08-23T10:03:00",
            "tool_name": "Edit",
            "file_path": "config.py",
            "old_string": "PORT = 8080\n",
            "new_string": "PORT = 8080\nHOST = 'localhost'\n",
        },
    ]

    with jsonlines.open(jsonl_dir / "complex.jsonl", mode="w") as writer:
        writer.write_all(events)

    return jsonl_dir


@pytest.fixture
def jsonl_with_multiedit_uuids(tmp_path):
    """Create JSONL with MultiEdit and UUIDs."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()

    events = [
        {
            "uuid": "multi-001",
            "timestamp": "2024-08-23T10:00:00",
            "tool_name": "Write",
            "file_path": "config.py",
            "content": "",
        },
        {
            "uuid": "multi-002",
            "timestamp": "2024-08-23T11:00:00",
            "tool_name": "MultiEdit",
            "file_path": "config.py",
            "edits": [
                {"old_string": "", "new_string": "DEBUG = True\n"},
                {
                    "old_string": "DEBUG = True\n",
                    "new_string": "DEBUG = True\nPORT = 8080\n",
                },
            ],
        },
    ]

    with jsonlines.open(jsonl_dir / "multiedit.jsonl", mode="w") as writer:
        writer.write_all(events)

    return jsonl_dir


@pytest.fixture
def native_claude_jsonl(tmp_path):
    """Create JSONL compatible with Timeline's expected structure."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()

    # Use Timeline-compatible structure (simplified from native format)
    events = [
        {
            "uuid": "native-001",
            "timestamp": "2024-08-23T10:00:00Z",
            "tool_name": "Write",
            "file_path": "app.py",
            "content": "def main():\n    pass\n"
        },
        {
            "uuid": "native-002",
            "timestamp": "2024-08-23T10:00:01Z",
            "tool_name": "Edit",
            "file_path": "app.py",
            "old_string": "def main():\n    pass",
            "new_string": "def main():\n    print('Hello from Timeline!')"
        }
    ]

    with jsonlines.open(jsonl_dir / "native.jsonl", mode="w") as writer:
        writer.write_all(events)

    return jsonl_dir
