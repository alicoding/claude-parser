"""
Test export_for_mem0() functionality.

Following TDD: Write tests first, then implement.
"""

import pytest
from pathlib import Path
from claude_parser import load
from claude_parser.models import UserMessage, AssistantMessage, ToolUse, ToolResult, Summary


@pytest.fixture
def sample_jsonl_file(tmp_path):
    """Create a sample JSONL file for testing."""
    file = tmp_path / "sample.jsonl"
    content = [
        '{"type":"user","content":"Hello Claude","uuid":"msg-1","sessionId":"session-123","cwd":"/test/dir","gitBranch":"main"}',
        '{"type":"assistant","content":"Hello! How can I help?","uuid":"msg-2","sessionId":"session-123","parentUuid":"msg-1"}',
        '{"type":"tool_use","toolUseID":"tool-1","name":"Edit","parameters":{"file":"test.py"},"sessionId":"session-123"}',
        '{"type":"tool_result","toolUseID":"tool-1","toolUseResult":"File edited successfully","sessionId":"session-123"}',
        '{"type":"summary","summary":"User greeted Claude","leafUuid":"leaf-1"}',
        '{"type":"assistant","content":"This message has an error in it","uuid":"msg-3","sessionId":"session-123"}'
    ]
    file.write_text('\n'.join(content))
    return file


def test_export_for_mem0_basic(sample_jsonl_file):
    """Test basic export_for_mem0 with default settings."""
    conv = load(sample_jsonl_file)
    result = conv.export_for_mem0()
    
    # Should have mem0-compatible structure
    assert "messages" in result
    assert "metadata" in result
    assert isinstance(result["messages"], list)
    
    # Should filter out tools and meta by default
    for msg in result["messages"]:
        assert msg["role"] in ["user", "assistant"]
        assert "content" in msg
        # No tool uses or results
        assert not any(k in msg for k in ["tool_calls", "tool_result"])


def test_export_for_mem0_with_filters(sample_jsonl_file):
    """Test export_for_mem0 with various filter options."""
    conv = load(sample_jsonl_file)
    
    # Test with tools included
    result_with_tools = conv.export_for_mem0(include_tools=True)
    messages = result_with_tools["messages"]
    
    # Should include tool-related messages
    tool_msgs = [m for m in messages if m.get("type") in ["tool_use", "tool_result"]]
    assert len(tool_msgs) > 0 if any(isinstance(m, (ToolUse, ToolResult)) for m in conv.messages) else True
    
    # Test with meta included
    result_with_meta = conv.export_for_mem0(include_meta=True)
    meta_msgs = [m for m in result_with_meta["messages"] if m.get("meta", False)]
    # Meta messages should be included if present
    
    # Test with summaries included
    result_with_summaries = conv.export_for_mem0(include_summaries=True)
    summary_msgs = [m for m in result_with_summaries["messages"] if m.get("type") == "summary"]
    assert len(summary_msgs) > 0 if any(isinstance(m, Summary) for m in conv.messages) else True


def test_export_for_mem0_format():
    """Test that export format matches mem0 requirements."""
    from claude_parser.domain.entities.conversation import Conversation, ConversationMetadata
    
    # Create minimal conversation
    messages = [
        UserMessage(
            uuid="user-1",
            timestamp="2024-01-01T00:00:00Z",
            content="Hello"
        ),
        AssistantMessage(
            uuid="assistant-1", 
            timestamp="2024-01-01T00:00:01Z",
            content="Hi there!"
        ),
        ToolUse(
            uuid="tool-1",
            timestamp="2024-01-01T00:00:02Z",
            name="read_file",
            parameters={"path": "test.txt"}
        ),
        ToolResult(
            uuid="result-1",
            timestamp="2024-01-01T00:00:03Z",
            tool_use_result="File contents"
        )
    ]
    
    metadata = ConversationMetadata(
        session_id="test-session",
        filepath=Path("test.jsonl"),
        current_dir="/test",
        git_branch="main",
        message_count=4,
        error_count=0
    )
    
    conv = Conversation(messages, metadata)
    
    # Default export (no tools)
    result = conv.export_for_mem0()
    
    assert result["metadata"]["session_id"] == "test-session"
    assert result["metadata"]["message_count"] == 2  # Only user and assistant
    assert len(result["messages"]) == 2
    
    # Check message format
    assert result["messages"][0] == {
        "role": "user",
        "content": "Hello",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    assert result["messages"][1] == {
        "role": "assistant", 
        "content": "Hi there!",
        "timestamp": "2024-01-01T00:00:01Z"
    }
    
    # With tools included
    result_with_tools = conv.export_for_mem0(include_tools=True)
    assert len(result_with_tools["messages"]) == 4
    assert result_with_tools["messages"][2]["type"] == "tool_use"
    assert result_with_tools["messages"][3]["type"] == "tool_result"


def test_export_for_mem0_empty_conversation():
    """Test export with empty conversation."""
    from claude_parser.domain.entities.conversation import Conversation, ConversationMetadata
    
    metadata = ConversationMetadata(
        session_id="empty",
        filepath=Path("empty.jsonl"),
        current_dir="/test",
        git_branch="main",
        message_count=0,
        error_count=0
    )
    
    conv = Conversation([], metadata)
    result = conv.export_for_mem0()
    
    assert result["messages"] == []
    assert result["metadata"]["message_count"] == 0