"""Test validation against REAL Claude Code JSON format.

This test ensures our HookData model works with actual Claude Code output,
not just theoretical schema.

Bug Report: https://github.com/anthropic/claude-code/issues/schema-mismatch
"""

import pytest

from claude_parser.hooks.models import HookData


class TestRealClaudeFormatCompatibility:
    """Test against actual Claude Code JSON samples."""

    def test_real_post_tool_use_format(self):
        """Test real PostToolUse JSON from Claude Code."""
        # Actual JSON from Claude Code bug report
        real_claude_json = {
            "hookEventName": "PostToolUse",
            "toolName": "Edit",
            "toolInput": {
                "file_path": "/path/to/file.md",
                "old_string": "old content",
                "new_string": "new content",
            },
            "toolResponse": [  # NOTE: List[Dict], not Dict!
                {
                    "type": "text",
                    "text": "Successfully applied 1 edit to /path/to/file.md",
                }
            ],
            "sessionId": "abc123",
            "transcriptPath": "/Users/ali/.claude/projects/session.jsonl",
            "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2",
        }

        # This should NOT raise ValidationError
        hook_data = HookData(**real_claude_json)

        # Verify all fields are accessible via snake_case
        assert hook_data.session_id == "abc123"
        assert hook_data.transcript_path == "/Users/ali/.claude/projects/session.jsonl"
        assert hook_data.hook_event_name == "PostToolUse"
        assert hook_data.tool_name == "Edit"
        assert hook_data.tool_input["file_path"] == "/path/to/file.md"

        # Verify tool_response handles List[Dict] format
        assert isinstance(hook_data.tool_response, list)
        assert hook_data.tool_response[0]["type"] == "text"
        assert "Successfully applied" in hook_data.tool_response[0]["text"]

    def test_real_stop_hook_format(self):
        """Test real Stop hook JSON from Claude Code."""
        real_stop_json = {
            "hookEventName": "Stop",
            "sessionId": "xyz789",
            "transcriptPath": "/Users/ali/.claude/projects/session.jsonl",
            "cwd": "/home/user/project",
        }

        hook_data = HookData(**real_stop_json)

        assert hook_data.hook_event_name == "Stop"
        assert hook_data.session_id == "xyz789"
        assert hook_data.tool_name is None  # No tool for Stop hook
        assert hook_data.tool_response is None

    def test_real_pre_tool_use_format(self):
        """Test real PreToolUse JSON from Claude Code."""
        real_pre_tool_json = {
            "hookEventName": "PreToolUse",
            "toolName": "Bash",
            "toolInput": {
                "command": "ls -la",
                "description": "List files in current directory",
            },
            "sessionId": "def456",
            "transcriptPath": "/Users/ali/.claude/projects/session.jsonl",
            "cwd": "/home/user/project",
        }

        hook_data = HookData(**real_pre_tool_json)

        assert hook_data.hook_event_name == "PreToolUse"
        assert hook_data.tool_name == "Bash"
        assert hook_data.tool_input["command"] == "ls -la"
        assert hook_data.tool_response is None  # No response in PreToolUse

    def test_camel_case_and_snake_case_both_work(self):
        """Test that both camelCase (Claude) and snake_case (Python) work."""
        # Claude format (camelCase)
        claude_format = {
            "hookEventName": "Stop",
            "sessionId": "test123",
            "transcriptPath": "/path/to/transcript.jsonl",
            "cwd": "/path",
        }

        # Python format (snake_case)
        python_format = {
            "hook_event_name": "Stop",
            "session_id": "test123",
            "transcript_path": "/path/to/transcript.jsonl",
            "cwd": "/path",
        }

        # Both should work and produce identical objects
        claude_data = HookData(**claude_format)
        python_data = HookData(**python_format)

        assert claude_data.session_id == python_data.session_id
        assert claude_data.hook_event_name == python_data.hook_event_name
        assert claude_data.transcript_path == python_data.transcript_path

    def test_tool_response_dict_format_still_works(self):
        """Ensure Dict format still works (backward compatibility)."""
        dict_format = {
            "hookEventName": "PostToolUse",
            "toolName": "Write",
            "toolResponse": {  # Dict format (legacy)
                "type": "text",
                "text": "File written successfully",
            },
            "sessionId": "test456",
            "transcriptPath": "/path/to/transcript.jsonl",
            "cwd": "/path",
        }

        hook_data = HookData(**dict_format)

        # Should handle Dict format too
        assert isinstance(hook_data.tool_response, dict)
        assert hook_data.tool_response["type"] == "text"

    def test_hook_type_property_alias(self):
        """Test convenience alias for hook_event_name."""
        hook_data = HookData(
            hookEventName="PreToolUse",
            sessionId="test789",
            transcriptPath="/path/to/transcript.jsonl",
            cwd="/path",
        )

        # Both should return the same value
        assert hook_data.hook_type == "PreToolUse"
        assert hook_data.hook_event_name == "PreToolUse"
        assert hook_data.hook_type == hook_data.hook_event_name

    def test_load_conversation_integration(self):
        """Test that load_conversation() works with real paths."""
        # Skip if real transcript doesn't exist
        real_transcript = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl"

        from pathlib import Path

        if not Path(real_transcript).exists():
            pytest.skip("Real transcript file not available")

        hook_data = HookData(
            hookEventName="PostToolUse",
            sessionId="real-test",
            transcriptPath=real_transcript,
            cwd="/path",
        )

        # This should load the actual conversation
        conv = hook_data.load_conversation()
        assert len(conv) > 0  # Should have messages

    def test_json_serialization_roundtrip(self):
        """Test that we can serialize and deserialize correctly."""
        original_data = {
            "hookEventName": "PostToolUse",
            "toolName": "Edit",
            "toolResponse": [{"type": "text", "text": "Success"}],
            "sessionId": "roundtrip-test",
            "transcriptPath": "/path/to/transcript.jsonl",
            "cwd": "/path",
        }

        # Parse with our model
        hook_data = HookData(**original_data)

        # Convert back to dict (should preserve camelCase aliases)
        serialized = hook_data.model_dump(by_alias=True)

        # Should be able to parse again
        roundtrip_data = HookData(**serialized)

        assert hook_data.session_id == roundtrip_data.session_id
        assert hook_data.hook_event_name == roundtrip_data.hook_event_name
