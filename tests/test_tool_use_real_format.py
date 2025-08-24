"""
TDD Tests for real Claude tool use format.
These tests should FAIL initially, then pass after fixing the implementation.
"""

import pytest
from pathlib import Path
from claude_parser import load
from claude_parser.models.tool import ToolUse


class TestRealToolUseFormat:
    """Test tool use extraction from real Claude JSONL format."""
    
    def test_assistant_tool_use_embedded_in_content(self, tmp_path):
        """
        TDD: Test that tool uses embedded in assistant message content are extracted.
        This test should FAIL initially because our current model doesn't handle this.
        """
        # Real format from Claude Code JSONL (single line)
        file = tmp_path / "real_tool.jsonl"
        real_tool_message = '{"type": "assistant", "timestamp": "2025-08-19T19:57:52.872Z", "sessionId": "session-123", "message": {"id": "msg_01", "type": "message", "role": "assistant", "content": [{"type": "tool_use", "id": "toolu_01WjRLjDnDtokN6LLSicWvy1", "name": "Bash", "input": {"command": "ls -la", "description": "List files"}}]}}'
        file.write_text(real_tool_message)
        
        # Load conversation
        conv = load(file)
        
        # This should FAIL initially - we expect tool uses to be found
        tool_uses = conv.tool_messages()
        assert len(tool_uses) > 0, "Should find tool use embedded in assistant message"
        
        # Verify tool details are extracted correctly
        tool = tool_uses[0]
        assert isinstance(tool, ToolUse)
        assert tool.tool_name == "Bash"
        assert tool.tool_use_id == "toolu_01WjRLjDnDtokN6LLSicWvy1"
        assert tool.parameters == {"command": "ls -la", "description": "List files"}
    
    def test_tool_result_embedded_in_user_content(self, tmp_path):
        """
        TDD: Test that tool results in user message content are extracted.
        This should FAIL initially.
        """
        file = tmp_path / "real_tool_result.jsonl"
        real_tool_result = '{"type": "user", "timestamp": "2025-08-19T19:57:52.872Z", "sessionId": "session-123", "message": {"role": "user", "content": [{"tool_use_id": "toolu_01WjRLjDnDtokN6LLSicWvy1", "type": "tool_result", "content": "total 8\\ndrwxr-xr-x  3 user  staff   96 Jan 20 11:00 .", "is_error": false}]}}'
        file.write_text(real_tool_result)
        
        # Load and test
        conv = load(file)
        
        # Should find the tool result
        tool_uses = conv.tool_messages()
        assert len(tool_uses) > 0, "Should find tool result embedded in user message"
        
        # Verify tool result details
        result = tool_uses[0]
        assert result.tool_use_id == "toolu_01WjRLjDnDtokN6LLSicWvy1"
        assert "total 8" in result.result_text
    
    def test_mixed_content_with_text_and_tools(self, tmp_path):
        """
        TDD: Test messages with both text and tool use content.
        Should FAIL initially.
        """
        file = tmp_path / "mixed_content.jsonl"
        mixed_message = '{"type": "assistant", "sessionId": "session-123", "message": {"content": [{"type": "text", "text": "I\'ll help you list the files."}, {"type": "tool_use", "id": "tool-123", "name": "Bash", "input": {"command": "ls"}}]}}'
        file.write_text(mixed_message)
        
        conv = load(file)
        
        # Should extract both text content and tool use
        assert len(conv.assistant_messages()) == 1
        assert len(conv.tool_uses) == 1
        
        # Text content should be accessible
        msg = conv.assistant_messages[0]
        assert "I'll help you list" in msg.text_content
        
        # Tool should be accessible
        tool = conv.tool_uses[0]
        assert tool.tool_name == "Bash"


class TestToolUseIntegration:
    """Test with real JSONL file to ensure we find actual tool uses."""
    
    def test_real_jsonl_finds_tools(self):
        """
        TDD: Test that real JSONL file shows tool uses.
        This should FAIL initially showing 0 tools.
        """
        real_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/2f283580-c24a-40af-8129-1be80c07b965.jsonl"
        
        if not Path(real_file).exists():
            pytest.skip("Real JSONL file not available")
        
        conv = load(real_file)
        
        # This should FAIL initially - we know there should be tools
        tool_count = len(conv.tool_uses)
        assert tool_count > 0, f"Should find tool uses in real file, found {tool_count}"
        
        # Should find a reasonable number (we saw at least 2 in investigation)
        assert tool_count >= 2, f"Should find at least 2 tool uses, found {tool_count}"
        
        print(f"✅ Found {tool_count} tool uses in real JSONL")