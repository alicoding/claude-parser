"""Integration tests with real Claude Code JSONL files."""

from pathlib import Path

import pytest

from claude_parser import MessageType, load

# Path to real Claude JSONL file for testing
# Real file path removed for privacy - tests use mock data instead
REAL_JSONL_PATH = "path/to/test.jsonl"  # Dummy path for tests to skip properly


class TestRealClaudeExport:
    """Test with actual Claude Code export file."""

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_load_real_claude_export(self):
        """Test loading actual Claude Code export."""
        conv = load(REAL_JSONL_PATH)

        # Basic assertions
        assert len(conv) > 0, "Should have messages"
        assert conv.session_id is not None, "Should have session ID"
        assert conv.messages is not None, "Should have messages list"

        # Verify message types exist
        types = {msg.type for msg in conv.messages}
        assert MessageType.USER in types or MessageType.ASSISTANT in types

        print(f"✅ Loaded {len(conv)} messages from real Claude export")

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_real_export_properties(self):
        """Test properties work with real export."""
        conv = load(REAL_JSONL_PATH)

        # Test all properties work without crashing
        user_msgs = conv.user_messages
        assistant_msgs = conv.assistant_messages
        tools = conv.tool_uses
        summaries = conv.summaries

        # Basic sanity checks
        assert isinstance(user_msgs, list)
        assert isinstance(assistant_msgs, list)
        assert isinstance(tools, list)
        assert isinstance(summaries, list)

        # Note: tool_uses includes embedded tools extracted from message content,
        # so total filtered count can exceed message count (this is expected!)
        total_base_messages = len(user_msgs) + len(assistant_msgs) + len(summaries)
        assert total_base_messages <= len(conv), "Base messages should not exceed total"
        assert len(tools) >= 0, "Should have non-negative tool count"

        print(
            f"✅ Properties work: {len(user_msgs)} user, {len(assistant_msgs)} assistant, {len(tools)} tools, {len(summaries)} summaries"
        )

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_real_export_search(self):
        """Test search functionality with real data."""
        conv = load(REAL_JSONL_PATH)

        # Try some realistic searches
        python_msgs = conv.search("python", case_sensitive=False)
        error_msgs = conv.with_errors()

        # Should not crash and should return lists
        assert isinstance(python_msgs, list)
        assert isinstance(error_msgs, list)

        # Results should be subsets of all messages
        assert len(python_msgs) <= len(conv)
        assert len(error_msgs) <= len(conv)

        print(
            f"✅ Search works: {len(python_msgs)} python mentions, {len(error_msgs)} error messages"
        )

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_real_export_navigation(self):
        """Test navigation features with real data."""
        conv = load(REAL_JSONL_PATH)

        # Test before_summary
        before = conv.messages_before_summary(10)
        assert isinstance(before, list)
        assert len(before) <= 10

        # Test metadata extraction
        cwd = conv.current_dir
        branch = conv.git_branch

        # These might be None but should not crash
        assert cwd is None or isinstance(cwd, str)
        assert branch is None or isinstance(branch, str)

        print(f"✅ Navigation works: {len(before)} messages before summary")
        if cwd:
            print(f"   Working dir: {cwd}")
        if branch:
            print(f"   Git branch: {branch}")

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_real_export_iteration(self):
        """Test iteration works with real data."""
        conv = load(REAL_JSONL_PATH)

        # Test basic iteration
        count = 0
        for msg in conv:
            count += 1
            assert hasattr(msg, "type")
            if count >= 10:  # Don't iterate through thousands
                break

        assert count == 10

        # Test indexing
        first = conv[0]
        last = conv[-1]
        middle = conv[len(conv) // 2]

        assert first is not None
        assert last is not None
        assert middle is not None

        # Test slicing
        first_10 = conv[0:10]
        assert len(first_10) == 10

        print("✅ Iteration and indexing work with real data")


class TestPerformance:
    """Test performance with real files."""

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_loading_performance(self):
        """Test that loading is reasonably fast."""
        import time

        start_time = time.time()
        conv = load(REAL_JSONL_PATH)
        load_time = time.time() - start_time

        # Should load a few thousand messages in under 2 seconds
        assert load_time < 2.0, f"Loading took {load_time:.2f}s, should be < 2s"

        print(f"✅ Performance: Loaded {len(conv)} messages in {load_time:.3f}s")

    @pytest.mark.skipif(
        not Path(REAL_JSONL_PATH).exists(),
        reason="Real Claude JSONL file not available",
    )
    def test_memory_usage_reasonable(self):
        """Test memory usage is reasonable."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        conv = load(REAL_JSONL_PATH)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = final_memory - initial_memory

        # File is ~10MB, should use less than 50MB total
        file_size = Path(REAL_JSONL_PATH).stat().st_size / 1024 / 1024  # MB

        assert memory_used < file_size * 5, (
            f"Used {memory_used:.1f}MB for {file_size:.1f}MB file"
        )

        print(
            f"✅ Memory: Used {memory_used:.1f}MB for {file_size:.1f}MB file ({len(conv)} messages)"
        )


class TestEdgeCases:
    """Test edge cases that might appear in real files."""

    def test_empty_messages_handled(self, tmp_path):
        """Test handling of empty or minimal messages."""
        file = tmp_path / "minimal.jsonl"
        content = [
            '{"type":"user","uuid":"u1","session_id":"s1","message":{"role":"user","content":""}}',  # Empty user message
            '{"type":"assistant","uuid":"a1","session_id":"s1","message":{"role":"assistant","content":""}}',  # Empty assistant
            '{"type":"summary","uuid":"sum1","session_id":"s1","summary":"test","leafUuid":"123"}',  # Minimal summary
        ]
        file.write_text("\n".join(content))

        conv = load(file)
        assert len(conv) == 3

        # Should not crash on empty content
        assert conv.user_messages[0].text_content == ""
        assert conv.assistant_messages[0].text_content == ""
        assert conv.summaries[0].text_content == "Summary: test"  # Summary adds prefix

    def test_unicode_and_special_chars(self, tmp_path):
        """Test Unicode and special characters."""
        file = tmp_path / "unicode.jsonl"
        content = [
            '{"type":"user","uuid":"u1","session_id":"s1","message":{"role":"user","content":"Hello 👋 世界! How about math: ∑ ∞ ≈ π?"}}',
            '{"type":"assistant","uuid":"a1","session_id":"s1","message":{"role":"assistant","content":"I can handle émojis 🚀 and ñoñô characters!"}}',
        ]
        file.write_text("\n".join(content))

        conv = load(file)
        assert len(conv) == 2

        # Content should be preserved exactly
        assert "👋 世界" in conv.user_messages[0].text_content
        assert "🚀" in conv.assistant_messages[0].text_content
        assert "ñoñô" in conv.assistant_messages[0].text_content
