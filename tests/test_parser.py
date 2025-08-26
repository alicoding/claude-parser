"""Tests for JSONL parser."""

import orjson
import pytest

from claude_parser.infrastructure.jsonl_parser import (
    count_messages,
    parse_jsonl,
    parse_jsonl_streaming,
    validate_jsonl,
)


class TestParseJsonl:
    """Test JSONL parsing."""

    def test_parse_valid_jsonl(self, tmp_path):
        """Test parsing valid JSONL file."""
        file = tmp_path / "test.jsonl"
        file.write_text(
            '{"type":"user","content":"Hi"}\n{"type":"assistant","content":"Hello"}'
        )

        messages = parse_jsonl(file)
        assert len(messages) == 2
        assert messages[0]["type"] == "user"
        assert messages[0]["content"] == "Hi"
        assert messages[1]["type"] == "assistant"

    def test_parse_empty_file(self, tmp_path):
        """Test parsing empty file."""
        file = tmp_path / "empty.jsonl"
        file.touch()

        messages = parse_jsonl(file)
        assert messages == []

    def test_parse_with_empty_lines(self, tmp_path):
        """Test parsing file with empty lines."""
        file = tmp_path / "test.jsonl"
        file.write_text(
            '{"type":"user","content":"Hi"}\n\n\n{"type":"assistant","content":"Hello"}\n'
        )

        messages = parse_jsonl(file)
        assert len(messages) == 2

    def test_parse_malformed_json(self, tmp_path):
        """Test parsing file with malformed JSON."""
        file = tmp_path / "bad.jsonl"
        file.write_text(
            '{"type":"user","content":"Hi"}\n{invalid json}\n{"type":"assistant","content":"Hello"}'
        )

        messages = parse_jsonl(file)
        assert len(messages) == 2  # Should skip the invalid line
        assert messages[0]["type"] == "user"
        assert messages[1]["type"] == "assistant"

    def test_file_not_found(self):
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            parse_jsonl("nonexistent.jsonl")

    def test_parse_unicode(self, tmp_path):
        """Test parsing file with unicode characters."""
        file = tmp_path / "unicode.jsonl"
        file.write_text('{"type":"user","content":"Hello 👋 世界"}\n{"emoji":"🚀"}')

        messages = parse_jsonl(file)
        assert len(messages) == 2
        assert messages[0]["content"] == "Hello 👋 世界"
        assert messages[1]["emoji"] == "🚀"


class TestParseJsonlStreaming:
    """Test streaming JSONL parser."""

    def test_streaming_parse(self, tmp_path):
        """Test streaming parser."""
        file = tmp_path / "test.jsonl"
        file.write_text('{"n":1}\n{"n":2}\n{"n":3}')

        messages = list(parse_jsonl_streaming(file))
        assert len(messages) == 3
        assert messages[0]["n"] == 1
        assert messages[2]["n"] == 3

    def test_streaming_memory_efficient(self, tmp_path):
        """Test streaming doesn't load all into memory."""
        file = tmp_path / "large.jsonl"

        # Create a file with many lines
        with open(file, "wb") as f:
            for i in range(1000):
                line = orjson.dumps({"index": i, "data": "x" * 100})
                f.write(line + b"\n")

        # Should be able to iterate without loading all
        count = 0
        for msg in parse_jsonl_streaming(file):
            count += 1
            if count == 10:  # Stop early
                break

        assert count == 10


class TestCountMessages:
    """Test message counting."""

    def test_count_messages(self, tmp_path):
        """Test counting messages."""
        file = tmp_path / "test.jsonl"
        file.write_text('{"n":1}\n{"n":2}\n\n{"n":3}\n{bad}\n{"n":4}')

        count = count_messages(file)
        assert count == 4  # Should count only valid messages


class TestValidateJsonl:
    """Test JSONL validation."""

    def test_validate_valid_file(self, tmp_path):
        """Test validating valid file."""
        file = tmp_path / "valid.jsonl"
        file.write_text('{"type":"user"}\n{"type":"assistant"}')

        is_valid, errors = validate_jsonl(file)
        assert is_valid is True
        assert errors == []

    def test_validate_invalid_file(self, tmp_path):
        """Test validating file with errors."""
        file = tmp_path / "invalid.jsonl"
        file.write_text('{"valid":true}\n{invalid}\n{"valid":true}\n{bad json}')

        is_valid, errors = validate_jsonl(file)
        assert is_valid is False
        assert errors == [2, 4]  # Lines 2 and 4 are invalid
