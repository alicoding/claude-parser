"""Tests for advanced JSON output hook helpers.

Tests the json_output() function and advanced.allow()/deny()/ask() methods
to ensure they produce correct JSON for Claude Code hooks.
"""

from io import StringIO
from unittest.mock import patch

import orjson
import pytest

from claude_parser.hooks import advanced, json_output


class TestJsonOutput:
    """Test the json_output function."""

    def test_pretooluse_allow_format(self):
        """Test PreToolUse produces correct allow format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                json_output(
                    decision="allow", reason="Test reason", hook_type="PreToolUse"
                )

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            # PreToolUse uses special nested structure
            assert "hookSpecificOutput" in data
            assert data["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
            assert data["hookSpecificOutput"]["permissionDecision"] == "allow"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"] == "Test reason"
            )

    def test_pretooluse_deny_format(self):
        """Test PreToolUse produces correct deny format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                json_output(
                    decision="deny", reason="Security violation", hook_type="PreToolUse"
                )

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Security violation"
            )

    def test_pretooluse_ask_format(self):
        """Test PreToolUse produces correct ask format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                json_output(
                    decision="ask",
                    reason="User confirmation needed",
                    hook_type="PreToolUse",
                )

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "ask"

    def test_legacy_approve_to_allow_conversion(self):
        """Test legacy 'approve' converts to 'allow'."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    decision="approve",  # Legacy name
                    reason="OK",
                    hook_type="PreToolUse",
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)
            assert data["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_legacy_block_to_deny_conversion(self):
        """Test legacy 'block' converts to 'deny'."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    decision="block",  # Legacy name
                    reason="Blocked",
                    hook_type="PreToolUse",
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)
            assert data["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_posttooluse_format(self):
        """Test PostToolUse uses simple format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                json_output(
                    decision="continue", reason="Success", hook_type="PostToolUse"
                )

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            # PostToolUse uses simple format (not nested)
            assert "hookSpecificOutput" not in data
            assert data["decision"] == "continue"
            assert data["reason"] == "Success"

    def test_userpromptsubmit_with_context(self):
        """Test UserPromptSubmit can add additional context."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    decision="continue",
                    reason="OK",
                    hook_type="UserPromptSubmit",
                    additional_context="Extra context here",
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["decision"] == "continue"
            assert data["reason"] == "OK"
            assert "hookSpecificOutput" in data
            assert (
                data["hookSpecificOutput"]["additionalContext"] == "Extra context here"
            )

    def test_sessionstart_with_context(self):
        """Test SessionStart can add context."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    hook_type="SessionStart", additional_context="Welcome message"
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert "hookSpecificOutput" in data
            assert data["hookSpecificOutput"]["additionalContext"] == "Welcome message"

    def test_stop_format(self):
        """Test Stop hook format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    decision="prevent", reason="Must continue", hook_type="Stop"
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["decision"] == "prevent"
            assert data["reason"] == "Must continue"

    def test_default_format_for_unknown_hook(self):
        """Test unknown hook types use simple format."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(
                    decision="continue", reason="Default", hook_type="UnknownHook"
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)

            # Unknown hooks use simple format
            assert "hookSpecificOutput" not in data
            assert data["decision"] == "continue"
            assert data["reason"] == "Default"


class TestAdvancedHelpers:
    """Test the advanced helper methods."""

    def test_advanced_allow(self):
        """Test advanced.allow() helper."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                advanced.allow("Custom approval reason")

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "allow"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Custom approval reason"
            )

    def test_advanced_allow_default_reason(self):
        """Test advanced.allow() with default reason."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                advanced.allow()

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "allow"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Auto-approved"
            )

    def test_advanced_deny(self):
        """Test advanced.deny() helper."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                advanced.deny("Security issue detected")

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Security issue detected"
            )

    def test_advanced_deny_default_reason(self):
        """Test advanced.deny() with default reason."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                advanced.deny()

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Security violation"
            )

    def test_advanced_ask(self):
        """Test advanced.ask() helper."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit) as exc_info:
                advanced.ask("Please confirm this action")

            assert exc_info.value.code == 0
            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["permissionDecision"] == "ask"
            assert (
                data["hookSpecificOutput"]["permissionDecisionReason"]
                == "Please confirm this action"
            )

    def test_advanced_add_context_userprompt(self):
        """Test advanced.add_context() for UserPromptSubmit."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                advanced.add_context(
                    "Additional information", hook_type="UserPromptSubmit"
                )

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["decision"] == "continue"
            assert (
                data["hookSpecificOutput"]["additionalContext"]
                == "Additional information"
            )

    def test_advanced_add_context_sessionstart(self):
        """Test advanced.add_context() for SessionStart."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                advanced.add_context("Welcome!", hook_type="SessionStart")

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["hookSpecificOutput"]["additionalContext"] == "Welcome!"

    def test_advanced_prevent(self):
        """Test advanced.prevent() for Stop hooks."""
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                advanced.prevent("Cannot stop now")

            output = fake_out.getvalue()
            data = orjson.loads(output)

            assert data["decision"] == "prevent"
            assert data["reason"] == "Cannot stop now"

    def test_json_output_always_exits_zero(self):
        """Test that json_output always exits with code 0."""
        test_cases = [
            ("PreToolUse", "allow"),
            ("PreToolUse", "deny"),
            ("PostToolUse", "continue"),
            ("Stop", "prevent"),
        ]

        for hook_type, decision in test_cases:
            with patch("sys.stdout", new=StringIO()):
                with pytest.raises(SystemExit) as exc_info:
                    json_output(decision=decision, hook_type=hook_type)

                assert exc_info.value.code == 0, f"Failed for {hook_type}/{decision}"

    def test_json_output_uses_orjson(self):
        """Verify we're using orjson for JSON serialization."""
        # This test verifies the output is valid orjson
        with patch("sys.stdout", new=StringIO()) as fake_out:
            with pytest.raises(SystemExit):
                json_output(decision="allow", reason="Test", hook_type="PreToolUse")

            output = fake_out.getvalue()
            # orjson.loads should parse it without issues
            data = orjson.loads(output)
            assert isinstance(data, dict)
