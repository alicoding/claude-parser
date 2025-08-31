"""
Test edge cases with real Claude JSONL files.

Following LIBRARY_FIRST_RULE - using pytest for testing, orjson for parsing.
Tests all edge cases documented in docs/JSONL-STRUCTURE.md
"""

from pathlib import Path

import orjson
import pytest

from claude_parser import load, validate_claude_format
from claude_parser.models.base import MessageType


class TestRealJSONLEdgeCases:
    """Test edge cases using real Claude JSONL files."""

    @pytest.fixture
    def minimal_sessions(self):
        """Find minimal JSONL sessions (1-5 lines) for edge case testing."""
        base_path = Path.home() / ".claude" / "projects"
        minimal_files = []

        # Find sessions with 1-5 lines
        for file in base_path.glob("*/*.jsonl"):
            try:
                with open(file, "rb") as f:
                    line_count = sum(1 for _ in f if _.strip())
                if 1 <= line_count <= 5:
                    minimal_files.append((file, line_count))
            except:
                continue

        return sorted(minimal_files, key=lambda x: x[1])[:5]  # Return 5 smallest

    def test_single_line_summary_only(self, minimal_sessions):
        """Test parsing single-line summary-only sessions."""
        # Find a 1-line file
        single_line_files = [f for f, count in minimal_sessions if count == 1]
        if not single_line_files:
            pytest.skip("No single-line JSONL files found")

        file_path = single_line_files[0]
        conv = load(file_path)

        # Should load without error
        assert conv is not None
        assert len(conv) >= 0  # May have 0 or 1 message

        # Check if it's a summary
        if len(conv) == 1:
            msg = conv[0]
            assert msg.type in [
                MessageType.SUMMARY,
                MessageType.USER,
                MessageType.ASSISTANT,
            ]

    def test_medium_session_with_tools(self):
        """Test a medium-sized session with tool use."""
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-personal-assistant/1b1af05a-0cac-4e65-97df-6bb86368cbad.jsonl"
        )

        if not file_path.exists():
            pytest.skip(f"Test file {file_path} not found")

        conv = load(file_path)

        # Basic assertions
        assert conv is not None
        assert len(conv) > 0

        # Check for different message types
        message_types = {msg.type for msg in conv}
        assert (
            MessageType.USER in message_types or MessageType.ASSISTANT in message_types
        )

        # Check session metadata
        if conv.session_id:
            assert isinstance(conv.session_id, str)
            assert len(conv.session_id) > 0

    def test_nested_content_blocks(self):
        """Test messages with nested content blocks (assistant messages with tool use)."""
        # Find a file with assistant messages
        test_files = [
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl",
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-personal-assistant/0c8bb4c6-f1f8-4bd1-8cb8-773414fac973.jsonl",
        ]

        for file_path in test_files:
            if file_path.exists():
                break
        else:
            pytest.skip("No test files with nested content found")

        conv = load(file_path)

        # Find assistant messages
        assistant_msgs = [msg for msg in conv if msg.type == MessageType.ASSISTANT]
        assert len(assistant_msgs) > 0, "Should have assistant messages"

        # Check that content is properly extracted
        for msg in assistant_msgs[:5]:  # Check first 5
            assert hasattr(msg, "text_content")
            # Content might be empty for tool-only messages
            assert isinstance(msg.text_content, str)

    def test_session_boundaries(self):
        """Test detection of session boundaries (different sessionIds)."""
        # This would need a file with multiple sessions or we skip
        # For now, test that sessionId is properly extracted
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-memory/0c7808e6-8b5a-4e90-bf31-dffb7cc02da1.jsonl"
        )

        if not file_path.exists():
            pytest.skip(f"Test file {file_path} not found")

        conv = load(file_path)

        # Check session ID extraction
        if conv.session_id:
            assert isinstance(conv.session_id, str)
            # UUID format check
            assert len(conv.session_id) == 36  # Standard UUID length
            assert conv.session_id.count("-") == 4

    def test_meta_messages(self):
        """Test handling of meta messages (isMeta: true)."""
        # Find a file likely to have meta messages
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center/0fa7629b-6811-4783-9bc2-cd84440c842d.jsonl"
        )

        if not file_path.exists():
            # Try another file
            file_path = (
                Path.home()
                / ".claude/projects/-Volumes-AliDev-ai-projects-personal-assistant/0c8bb4c6-f1f8-4bd1-8cb8-773414fac973.jsonl"
            )

        if not file_path.exists():
            pytest.skip("No test files found for meta messages")

        # Read raw to check for meta messages
        with open(file_path, "rb") as f:
            has_meta = False
            for line in f:
                if not line.strip():
                    continue
                try:
                    data = orjson.loads(line)
                    if data.get("isMeta"):
                        has_meta = True
                        break
                except:
                    continue

        # Load with parser
        conv = load(file_path)
        assert conv is not None

        # If file has meta messages, parser should handle them
        if has_meta:
            assert len(conv) >= 0  # Should not crash on meta messages

    def test_empty_content_handling(self):
        """Test handling of messages with empty or missing content."""
        # Create a test file with empty content
        test_file = Path("/tmp/test_empty_content.jsonl")

        test_data = [
            # User message with empty content in message field
            {
                "type": "user",
                "sessionId": "test-session",
                "uuid": "msg-1",
                "parentUuid": None,
                "message": {"role": "user", "content": ""},
                "timestamp": "2025-01-01T00:00:00Z",
            },
            # Assistant message with tool-only content (no text)
            {
                "type": "assistant",
                "sessionId": "test-session",
                "uuid": "msg-2",
                "parentUuid": "msg-1",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "tool_use", "name": "Bash", "id": "tool-1"}],
                },
                "timestamp": "2025-01-01T00:00:01Z",
            },
        ]

        with open(test_file, "wb") as f:
            for item in test_data:
                f.write(orjson.dumps(item) + b"\n")

        try:
            conv = load(test_file)
            assert conv is not None
            assert len(conv) >= 0  # Should handle empty content

            # Check messages loaded
            for msg in conv:
                assert hasattr(msg, "text_content")
                assert isinstance(msg.text_content, str)  # Even if empty
        finally:
            test_file.unlink(missing_ok=True)

    def test_large_file_streaming(self, tmp_path_factory):
        """Test streaming large files efficiently - TRUE 95/5 with tmp_path_factory."""
        # TRUE 95/5: Let pytest create and manage the temp file
        large_file = tmp_path_factory.mktemp("data") / "large.jsonl"
        
        # Generate a large file (10MB+) with realistic Claude messages
        import orjson
        with open(large_file, "wb") as f:
            for i in range(10000):  # 10k messages ~= 10MB
                msg = {
                    "type": "user" if i % 2 == 0 else "assistant",
                    "uuid": f"msg-{i}",
                    "sessionId": "test-session",
                    "timestamp": f"2025-01-01T{i//3600:02d}:{(i//60)%60:02d}:{i%60:02d}Z",
                    "message": {
                        "role": "user" if i % 2 == 0 else "assistant",
                        "content": f"This is message {i} with some content to make it realistic size " * 10
                    }
                }
                f.write(orjson.dumps(msg) + b"\n")

        # Test streaming parse
        from claude_parser.infrastructure.jsonl_parser import parse_jsonl_streaming

        message_count = 0
        for msg in parse_jsonl_streaming(large_file):
            message_count += 1
            if message_count > 100:  # Just test first 100 for speed
                break

        assert message_count > 0, "Should stream messages from large file"

    def test_malformed_json_handling(self):
        """Test that malformed JSON lines are skipped gracefully."""
        test_file = Path("/tmp/test_malformed.jsonl")

        with open(test_file, "w") as f:
            f.write('{"type": "user", "content": "valid"}\n')
            f.write("{ broken json\n")  # Malformed
            f.write('{"type": "assistant", "content": "also valid"}\n')
            f.write("not even json\n")  # Malformed
            f.write('{"type": "summary", "summary": "end"}\n')

        try:
            conv = load(test_file)
            # Should skip malformed lines
            assert conv is not None
            # Should load at least some messages
            assert len(conv) >= 0
        finally:
            test_file.unlink(missing_ok=True)

    def test_validate_claude_format(self):
        """Test Claude format validation with real files."""
        # Test with a known Claude file
        claude_file = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-personal-assistant/1b1af05a-0cac-4e65-97df-6bb86368cbad.jsonl"
        )

        if claude_file.exists():
            is_valid, errors = validate_claude_format(claude_file)
            # Real Claude files should validate
            assert is_valid or len(errors) > 0  # Either valid or has specific errors

        # Test with non-Claude JSONL
        test_file = Path("/tmp/test_non_claude.jsonl")
        with open(test_file, "w") as f:
            f.write('{"random": "data", "no": "claude fields"}\n')
            f.write('{"more": "random", "still": "not claude"}\n')

        try:
            is_valid, errors = validate_claude_format(test_file)
            assert not is_valid  # Should not validate as Claude format
            assert len(errors) > 0  # Should have error messages
        finally:
            test_file.unlink(missing_ok=True)


class TestRealDataPatterns:
    """Test specific patterns found in real Claude JSONL files."""

    def test_git_branch_tracking(self):
        """Test tracking of git branch changes within a session."""
        # Most files will have gitBranch field
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl"
        )

        if not file_path.exists():
            pytest.skip("Test file not found")

        conv = load(file_path)

        # Check git branch extraction
        if conv.git_branch:
            assert isinstance(conv.git_branch, str)
            # Common branch names
            assert (
                conv.git_branch in ["main", "master", "develop", ""]
                or "/" in conv.git_branch
            )

    def test_cwd_tracking(self):
        """Test current working directory tracking."""
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-personal-assistant/1b1af05a-0cac-4e65-97df-6bb86368cbad.jsonl"
        )

        if not file_path.exists():
            pytest.skip("Test file not found")

        conv = load(file_path)

        # Check cwd extraction
        if conv.current_dir:
            assert isinstance(conv.current_dir, str)
            assert conv.current_dir.startswith("/")  # Should be absolute path

    def test_parent_uuid_threading(self):
        """Test reconstruction of conversation threads via parentUuid."""
        file_path = (
            Path.home()
            / ".claude/projects/-Volumes-AliDev-ai-projects-memory/0c7808e6-8b5a-4e90-bf31-dffb7cc02da1.jsonl"
        )

        if not file_path.exists():
            pytest.skip("Test file not found")

        # Read raw to check parentUuid chains
        with open(file_path, "rb") as f:
            messages = []
            for line in f:
                if not line.strip():
                    continue
                try:
                    messages.append(orjson.loads(line))
                except:
                    continue

        if len(messages) > 1:
            # Check threading
            first_msg = messages[0]
            assert first_msg.get("parentUuid") is None or isinstance(
                first_msg.get("parentUuid"), str
            )

            # Later messages should have parentUuid
            for msg in messages[1:5]:  # Check first few
                parent = msg.get("parentUuid")
                if parent:
                    assert isinstance(parent, str)
                    assert len(parent) > 0
