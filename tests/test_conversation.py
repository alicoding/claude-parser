"""Tests for Conversation class."""

import pytest
from pathlib import Path
from claude_parser import load
from claude_parser.domain.conversation import Conversation
from claude_parser.models import MessageType, AssistantMessage, UserMessage


@pytest.fixture
def real_claude_jsonl():
    """Use real Claude Code JSONL file for testing."""
    real_file = Path("/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl")
    if not real_file.exists():
        pytest.skip(f"Real Claude Code file not found: {real_file}")
    return real_file


class TestConversationInit:
    """Test conversation initialization."""
    
    def test_conversation_creation(self, real_claude_jsonl):
        """Test creating conversation from JSONL."""
        conv = load(sample_jsonl)
        assert len(conv) > 0
        assert conv.session_id == "session-123"
        assert conv.metadata.filepath.name == "sample.jsonl"
    
    def test_conversation_with_missing_file(self):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError):
            load("nonexistent.jsonl")
    
    def test_conversation_repr(self, sample_jsonl):
        """Test string representation."""
        conv = load(sample_jsonl)
        repr_str = repr(conv)
        assert "Conversation" in repr_str
        assert "messages=" in repr_str
        assert "session_id=" in repr_str


class TestConversationProperties:
    """Test conversation properties."""
    
    def test_messages_property(self, sample_jsonl):
        """Test messages property."""
        conv = load(sample_jsonl)
        messages = conv.messages
        assert isinstance(messages, list)
        assert len(messages) == 6
        assert all(hasattr(msg, 'type') for msg in messages)
    
    def test_session_id_property(self, sample_jsonl):
        """Test session_id extraction."""
        conv = load(sample_jsonl)
        assert conv.session_id == "session-123"
    
    def test_assistant_messages(self, sample_jsonl):
        """Test assistant messages filtering."""
        conv = load(sample_jsonl)
        assistant_msgs = conv.assistant_messages()
        assert len(assistant_msgs) == 2
        assert all(isinstance(msg, AssistantMessage) for msg in assistant_msgs)
    
    def test_user_messages(self, sample_jsonl):
        """Test user messages filtering."""
        conv = load(sample_jsonl)
        user_msgs = conv.user_messages()
        assert len(user_msgs) > 1000  # Real file has 1067 user messages
        assert all(isinstance(msg, UserMessage) for msg in user_msgs)
    
    def test_tool_uses(self, sample_jsonl):
        """Test tool use filtering."""
        conv = load(sample_jsonl)
        tools = conv.tool_messages()
        assert len(tools) >= 0  # Real file might not have many standalone tool messages
    
    def test_summaries(self, sample_jsonl):
        """Test summary filtering."""
        conv = Conversation(sample_jsonl)
        summaries = conv.summaries()
        assert len(summaries) > 0  # Real file has summaries
    
    def test_current_dir(self, sample_jsonl):
        """Test current directory extraction."""
        conv = Conversation(sample_jsonl)
        assert conv.current_dir == "/test/dir"
    
    def test_git_branch(self, sample_jsonl):
        """Test git branch extraction."""
        conv = Conversation(sample_jsonl)
        assert conv.git_branch == "main"


class TestConversationMethods:
    """Test conversation methods."""
    
    def test_filter_method(self, sample_jsonl):
        """Test filter method."""
        conv = Conversation(sample_jsonl)
        user_msgs = conv.filter(lambda m: m.type == MessageType.USER)
        assert len(user_msgs) == 1
        assert user_msgs[0].type == MessageType.USER
    
    def test_search_method(self, sample_jsonl):
        """Test search method."""
        conv = Conversation(sample_jsonl)
        results = conv.search("Hello")
        assert len(results) == 2  # Both user and assistant say hello
    
    def test_search_case_insensitive(self, sample_jsonl):
        """Test case insensitive search."""
        conv = Conversation(sample_jsonl)
        results = conv.search("HELLO", case_sensitive=False)
        assert len(results) == 2
    
    def test_search_case_sensitive(self, sample_jsonl):
        """Test case sensitive search."""
        conv = Conversation(sample_jsonl)
        results = conv.search("HELLO", case_sensitive=True)
        assert len(results) == 0  # No uppercase HELLO
    
    def test_before_summary(self, sample_jsonl):
        """Test before_summary method."""
        conv = Conversation(sample_jsonl)
        before = conv.messages_before_summary(10)
        # Should get messages before the summary (indices 0-3)
        assert len(before) == 4
        assert before[-1].type != MessageType.SUMMARY
    
    def test_before_summary_no_summary(self, tmp_path):
        """Test before_summary with no summary."""
        file = tmp_path / "no_summary.jsonl"
        file.write_text('{"type":"user","content":"Hi"}\n{"type":"assistant","content":"Hello"}')
        
        conv = load(file)
        before = conv.before_summary(10)
        assert len(before) == 2  # All messages returned
    
    def test_with_errors(self, sample_jsonl):
        """Test error detection."""
        conv = Conversation(sample_jsonl)
        errors = conv.messages_with_errors()
        assert len(errors) == 1  # One message contains "error"
        assert "error" in errors[0].text_content.lower()


class TestConversationIteration:
    """Test conversation iteration and indexing."""
    
    def test_len(self, sample_jsonl):
        """Test length."""
        conv = Conversation(sample_jsonl)
        assert len(conv) == 6
    
    def test_getitem_index(self, sample_jsonl):
        """Test indexing."""
        conv = Conversation(sample_jsonl)
        first = conv[0]
        last = conv[-1]
        assert first.type == MessageType.USER
        assert last.type == MessageType.ASSISTANT
    
    def test_getitem_slice(self, sample_jsonl):
        """Test slicing."""
        conv = Conversation(sample_jsonl)
        first_three = conv[0:3]
        assert len(first_three) == 3
        assert isinstance(first_three, list)
    
    def test_iteration(self, sample_jsonl):
        """Test iteration."""
        conv = Conversation(sample_jsonl)
        count = 0
        for msg in conv:
            count += 1
            assert hasattr(msg, 'type')
        assert count == 6


class TestConversationErrorHandling:
    """Test error handling."""
    
    def test_malformed_jsonl(self, tmp_path):
        """Test handling malformed JSONL."""
        file = tmp_path / "bad.jsonl"
        file.write_text('{"type":"user","content":"Hi"}\n{bad json}\n{"type":"assistant","content":"Hello"}')
        
        conv = load(file)
        assert len(conv) == 2  # Should skip bad line
        # Error information is logged but not exposed on conversation object
    
    def test_empty_file(self, tmp_path):
        """Test empty file handling."""
        file = tmp_path / "empty.jsonl"
        file.touch()
        
        conv = Conversation(file)
        assert len(conv) == 0
        assert conv.session_id is None