"""Test for critical bug fix: tool_response accepting strings.

BUG REPORT: Claude sends string responses for many tools (LS, Grep, Read, etc.)
but claude-parser only accepted Dict or List[Dict].

This test validates the fix using real Claude output examples.
"""

import json
import pytest
from claude_parser.hooks.models import HookData


class TestToolResponseStringBug:
    """Test that tool_response correctly handles all formats."""
    
    def test_ls_tool_returns_string(self):
        """LS tool returns formatted directory listing as string."""
        # Real Claude output from bug report
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "LS",
            "toolResponse": "- /Users/ali/.claude/projects/\n  - file.md\n  - subdir/\n"  # STRING!
        }
        
        # Should not raise validation error
        data = HookData(**hook_data)
        assert data.tool_name == "LS"
        assert isinstance(data.tool_response, str)
        assert "file.md" in data.tool_response
    
    def test_grep_tool_returns_string(self):
        """Grep tool returns search results as string."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "Grep",
            "toolResponse": "file.ts:10: const result = parseMessage(data)\nfile.ts:20: if (result.success) {"
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "Grep"
        assert isinstance(data.tool_response, str)
        assert "parseMessage" in data.tool_response
    
    def test_read_tool_returns_string(self):
        """Read tool returns file contents as string."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "Read",
            "toolResponse": "# README\n\nThis is the file content...\n\nMultiple lines of text."
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "Read"
        assert isinstance(data.tool_response, str)
        assert "README" in data.tool_response
    
    def test_bash_tool_returns_string(self):
        """Bash tool returns command output as string."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "Bash",
            "toolResponse": "npm test\n\n✓ 23 tests passed\n✓ 0 tests failed\n\nTest suite completed."
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "Bash"
        assert isinstance(data.tool_response, str)
        assert "tests passed" in data.tool_response
    
    def test_edit_tool_still_accepts_list_dict(self):
        """Edit tool can still return List[Dict] format."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "Edit",
            "toolResponse": [
                {"type": "text", "text": "File edited successfully"}
            ]
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "Edit"
        assert isinstance(data.tool_response, list)
        assert data.tool_response[0]["text"] == "File edited successfully"
    
    def test_custom_tool_still_accepts_dict(self):
        """Custom tools can still return Dict format."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "CustomTool",
            "toolResponse": {
                "status": "success",
                "data": {"result": 42}
            }
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "CustomTool"
        assert isinstance(data.tool_response, dict)
        assert data.tool_response["status"] == "success"
    
    def test_tool_response_can_be_none(self):
        """tool_response can be None/missing."""
        hook_data = {
            "sessionId": "abc123xyz",
            "transcriptPath": "/tmp/session.jsonl",
            "cwd": "/project",
            "hookEventName": "PostToolUse",
            "toolName": "SomeTool"
            # No toolResponse field
        }
        
        data = HookData(**hook_data)
        assert data.tool_response is None
    
    def test_real_world_ls_output(self):
        """Test with actual LS output from Claude."""
        # This is real output captured from Claude
        hook_data = {
            "sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
            "transcriptPath": "/Users/ali/.claude/projects/session.jsonl",
            "cwd": "/Users/ali/.claude/projects/claude-parser",
            "hookEventName": "PostToolUse",
            "toolName": "LS",
            "toolResponse": """- /Users/ali/.claude/projects/
  - claude-parser/
    - docs/
      - api/
        - CHANGELOG.md
        - QUICK_REFERENCE.md
        - README.md
        - hooks.md
        - parser.md
        - typescript-sdk.md
        - watch.md
    - claude_parser/
      - __init__.py
      - hooks/
        - models.py
        - input.py
        - exits.py"""
        }
        
        data = HookData(**hook_data)
        assert data.tool_name == "LS"
        assert isinstance(data.tool_response, str)
        assert "hooks.md" in data.tool_response
        assert "models.py" in data.tool_response