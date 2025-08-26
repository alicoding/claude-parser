"""
TDD Tests for Claude format validation.
These tests should FAIL initially, then pass after implementing validation.
"""

from pathlib import Path

import pytest

from claude_parser import load
from claude_parser.infrastructure.jsonl_parser import validate_claude_format


class TestClaudeFormatValidation:
    """Test Claude JSONL format validation."""

    def test_valid_claude_format_passes(self, tmp_path):
        """
        TDD: Test that valid Claude JSONL passes validation.
        Should FAIL initially - validate_claude_format doesn't exist yet.
        """
        file = tmp_path / "valid_claude.jsonl"

        # Real Claude format with session ID and typical structure
        claude_content = [
            '{"type": "user", "sessionId": "session-123", "timestamp": "2025-08-19T19:57:52.872Z", "message": {"role": "user", "content": [{"type": "text", "text": "Hello Claude"}]}}',
            '{"type": "assistant", "sessionId": "session-123", "timestamp": "2025-08-19T19:57:53.000Z", "message": {"role": "assistant", "content": [{"type": "text", "text": "Hello! How can I help?"}]}}',
            '{"type": "summary", "summary": "Greeting exchange", "leafUuid": "uuid-123"}',
        ]

        file.write_text("\n".join(claude_content))

        # This should FAIL initially - function doesn't exist
        is_valid, errors = validate_claude_format(file)

        assert is_valid is True, (
            f"Valid Claude format should pass validation. Errors: {errors}"
        )
        assert len(errors) == 0, f"Should have no validation errors, got: {errors}"

    def test_non_claude_jsonl_fails_validation(self, tmp_path):
        """
        TDD: Test that non-Claude JSONL fails validation.
        Should FAIL initially - validation not implemented.
        """
        file = tmp_path / "not_claude.jsonl"

        # Generic JSONL that isn't Claude format
        generic_content = [
            '{"id": 1, "name": "John", "age": 30}',
            '{"id": 2, "name": "Jane", "age": 25}',
            '{"message": "This is not Claude format"}',
        ]

        file.write_text("\n".join(generic_content))

        # Should detect this is not Claude format
        is_valid, errors = validate_claude_format(file)

        assert is_valid is False, "Non-Claude JSONL should fail validation"
        assert len(errors) > 0, "Should report validation errors"
        assert any("Claude" in error for error in errors), (
            f"Should mention Claude format in errors: {errors}"
        )

    def test_load_with_strict_validation(self, tmp_path):
        """
        TDD: Test load() with strict validation mode.
        Should FAIL initially - strict mode not implemented.
        """
        file = tmp_path / "invalid_claude.jsonl"

        # Invalid format (missing sessionId, wrong structure)
        invalid_content = [
            '{"type": "user", "content": "Missing sessionId"}',
            '{"type": "random", "data": "Unknown message type"}',
        ]

        file.write_text("\n".join(invalid_content))

        # Should raise ValueError in strict mode
        with pytest.raises(ValueError) as exc_info:
            load(file, strict=True)

        assert "Claude Code format" in str(exc_info.value), (
            "Should mention Claude Code format in error"
        )

    def test_load_without_strict_validation_works(self, tmp_path):
        """
        TDD: Test load() without strict validation (default).
        Should work as it does now - load whatever we can parse.
        """
        file = tmp_path / "mixed_format.jsonl"

        # Mixed format - some valid Claude, some generic
        mixed_content = [
            '{"type": "user", "uuid": "u1", "session_id": "session-123", "message": {"role": "user", "content": "Valid Claude"}}',
            '{"id": 1, "generic": "data"}',
            '{"type": "assistant", "uuid": "a1", "session_id": "session-123", "message": {"role": "assistant", "content": "Another valid Claude"}}',
        ]

        file.write_text("\n".join(mixed_content))

        # Should load successfully in non-strict mode (default behavior)
        conv = load(file, strict=False)

        # Should load the messages it can parse
        assert len(conv) >= 2, "Should load at least the valid Claude messages"

    def test_claude_format_signature_detection(self, tmp_path):
        """
        TDD: Test detection of Claude format signatures.
        Should FAIL initially - signature detection not implemented.
        """
        file = tmp_path / "claude_signature.jsonl"

        # File with Claude signatures but minimal content
        signature_content = [
            '{"sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75", "type": "user"}',  # sessionId format
            '{"type": "summary", "leafUuid": "uuid-format"}',  # leafUuid field
            '{"gitBranch": "main", "cwd": "/some/path", "type": "system"}',  # Claude metadata
        ]

        file.write_text("\n".join(signature_content))

        is_valid, errors = validate_claude_format(file)

        # Should recognize Claude signatures
        assert is_valid is True, (
            f"Should recognize Claude format signatures. Errors: {errors}"
        )

    def test_empty_file_validation(self, tmp_path):
        """
        TDD: Test validation of empty files.
        Should FAIL initially.
        """
        file = tmp_path / "empty.jsonl"
        file.write_text("")

        is_valid, errors = validate_claude_format(file)

        # Empty file should fail validation
        assert is_valid is False, "Empty file should fail validation"
        assert len(errors) > 0, "Should report error for empty file"


class TestRealClaudeFileValidation:
    """Test validation with real Claude export file."""

    def test_real_claude_file_passes_validation(self):
        """
        TDD: Test that real Claude export passes validation.
        Should FAIL initially.
        """
        real_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/2f283580-c24a-40af-8129-1be80c07b965.jsonl"

        if not Path(real_file).exists():
            pytest.skip("Real Claude JSONL file not available")

        # Real Claude file should definitely pass validation
        is_valid, errors = validate_claude_format(real_file)

        assert is_valid is True, (
            f"Real Claude file should pass validation. Errors: {errors}"
        )
        assert len(errors) == 0, (
            f"Real Claude file should have no validation errors: {errors}"
        )

        print("✅ Real Claude file validated successfully")
