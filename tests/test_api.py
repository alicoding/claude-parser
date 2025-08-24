"""Tests for public API - the 95% use cases."""

import pytest
from pathlib import Path
from claude_parser import load, load_many, Conversation, MessageType


@pytest.fixture
def simple_jsonl(tmp_path):
    """Simple JSONL for basic testing."""
    file = tmp_path / "simple.jsonl"
    content = [
        '{"type":"user","content":"Hello","uuid":"msg-1","sessionId":"test-session"}',
        '{"type":"assistant","content":"Hi there!","uuid":"msg-2","sessionId":"test-session"}',
        '{"type":"tool_use","toolUseID":"tool-1","name":"Read","sessionId":"test-session"}',
        '{"type":"tool_result","toolUseID":"tool-1","toolUseResult":"File contents","sessionId":"test-session"}'
    ]
    file.write_text('\n'.join(content))
    return file


class TestLoadFunction:
    """Test the main load() function - 95% use case."""
    
    def test_load_basic(self, simple_jsonl):
        """Test basic load functionality."""
        # This is the 95% use case - must be this simple!
        conv = load(simple_jsonl)
        
        # Basic assertions
        assert isinstance(conv, Conversation)
        assert len(conv.messages) == 4
        assert conv.session_id == "test-session"
    
    def test_load_with_string_path(self, simple_jsonl):
        """Test load with string path."""
        conv = load(str(simple_jsonl))
        assert len(conv) == 4
    
    def test_load_with_pathlib(self, simple_jsonl):
        """Test load with pathlib.Path."""
        conv = load(simple_jsonl)  # Already a Path object
        assert len(conv) == 4
    
    def test_load_file_not_found(self):
        """Test load with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load("nonexistent.jsonl")


class TestLoadManyFunction:
    """Test load_many() function."""
    
    def test_load_many(self, tmp_path):
        """Test loading multiple files."""
        # Create two simple files
        file1 = tmp_path / "conv1.jsonl"
        file1.write_text('{"type":"user","content":"Hello 1","sessionId":"session-1"}')
        
        file2 = tmp_path / "conv2.jsonl"
        file2.write_text('{"type":"user","content":"Hello 2","sessionId":"session-2"}')
        
        # Load both
        convs = load_many([file1, file2])
        
        assert len(convs) == 2
        assert len(convs[0]) == 1
        assert len(convs[1]) == 1
        assert convs[0].session_id == "session-1"
        assert convs[1].session_id == "session-2"
    
    def test_load_many_empty_list(self):
        """Test load_many with empty list."""
        convs = load_many([])
        assert convs == []


class Test95PercentUseCases:
    """Test the most common usage patterns."""
    
    def test_95_percent_pattern_basic(self, simple_jsonl):
        """Test the primary 95% use case pattern."""
        # This exact pattern must work with zero configuration
        conv = load(simple_jsonl)
        
        # Basic access patterns
        assert conv.messages is not None
        assert conv.session_id is not None
        assert len(conv) > 0
        assert conv[0] is not None
    
    def test_95_percent_pattern_properties(self, simple_jsonl):
        """Test common property access patterns."""
        conv = load(simple_jsonl)
        
        # These should all work without any setup
        assistant_msgs = conv.assistant_messages
        user_msgs = conv.user_messages
        tools = conv.tool_messages()
        
        assert len(assistant_msgs) == 1
        assert len(user_msgs) == 1
        assert len(tools) == 2  # tool_use + tool_result
    
    def test_95_percent_pattern_search(self, simple_jsonl):
        """Test common search patterns."""
        conv = load(simple_jsonl)
        
        # Simple search should work
        results = conv.search("Hello")
        assert len(results) == 1
        
        # Filter should work
        users = conv.filter(lambda m: m.type == MessageType.USER)
        assert len(users) == 1
    
    def test_95_percent_pattern_iteration(self, simple_jsonl):
        """Test iteration patterns."""
        conv = load(simple_jsonl)
        
        # These iteration patterns must work
        count = 0
        for msg in conv:
            count += 1
            assert hasattr(msg, 'type')
        assert count == 4
        
        # List comprehension must work
        types = [msg.type for msg in conv]
        assert len(types) == 4
    
    def test_95_percent_error_handling(self, tmp_path):
        """Test that errors don't break the 95% case."""
        # File with some bad lines should still work
        file = tmp_path / "mixed.jsonl"
        content = [
            '{"type":"user","content":"Good line"}',
            '{invalid json}',  # Bad line
            '{"type":"assistant","content":"Another good line"}',
        ]
        file.write_text('\n'.join(content))
        
        # Should still work - skip bad lines
        conv = load(file)
        assert len(conv) == 2  # Only good lines
        assert conv.messages[0].type == MessageType.USER
        assert conv.messages[1].type == MessageType.ASSISTANT


class TestAPIImports:
    """Test that important things can be imported."""
    
    def test_main_imports(self):
        """Test main imports work."""
        from claude_parser import load, load_many, Conversation
        
        assert callable(load)
        assert callable(load_many)
        assert Conversation is not None
    
    def test_message_type_imports(self):
        """Test message type imports."""
        from claude_parser import MessageType, UserMessage, AssistantMessage
        
        assert MessageType.USER == "user"
        assert UserMessage is not None
        assert AssistantMessage is not None
    
    def test_version_available(self):
        """Test version is available."""
        import claude_parser
        assert hasattr(claude_parser, '__version__')
        assert isinstance(claude_parser.__version__, str)


class TestRealWorldUsage:
    """Test real-world usage scenarios."""
    
    def test_typical_workflow(self, simple_jsonl):
        """Test a typical analysis workflow."""
        # Load conversation
        conv = load(simple_jsonl)
        
        # Analyze conversation
        user_count = len(conv.user_messages)
        assistant_count = len(conv.assistant_messages)
        tool_count = len(conv.tool_uses)
        
        # Get session info
        session = conv.session_id
        
        # Search for specific content
        greetings = conv.search("Hello")
        
        # All should work without issues
        assert user_count == 1
        assert assistant_count == 1
        assert tool_count == 2
        assert session == "test-session"
        assert len(greetings) == 1
    
    def test_one_liner_analysis(self, simple_jsonl):
        """Test one-liner analysis patterns."""
        # These should all work as one-liners
        total_messages = len(load(simple_jsonl).messages)
        session_id = load(simple_jsonl).session_id
        assistant_count = len(load(simple_jsonl).assistant_messages)
        
        assert total_messages == 4
        assert session_id == "test-session"  
        assert assistant_count == 1
    
    def test_chain_operations(self, simple_jsonl):
        """Test method chaining patterns."""
        conv = load(simple_jsonl)
        
        # Find user messages with specific content
        user_hellos = [msg for msg in conv.user_messages if "Hello" in msg.text_content]
        assert len(user_hellos) == 1
        
        # Get messages before any summary (none in this case)
        before_summary = conv.messages_before_summary(10)
        assert len(before_summary) == 4  # All messages since no summary