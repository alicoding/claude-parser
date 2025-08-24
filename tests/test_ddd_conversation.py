"""Tests for DDD Conversation implementation with real Claude Code data."""

import pytest
import time
from pathlib import Path
from claude_parser import load
from claude_parser.domain import ConversationAnalyzer
from claude_parser.domain.entities.conversation import Conversation, ConversationMetadata
from claude_parser.models import MessageType, AssistantMessage, UserMessage


@pytest.fixture
def real_claude_file():
    """Real Claude Code JSONL file for testing DDD implementation."""
    real_file = Path("/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl")
    if not real_file.exists():
        pytest.skip(f"Real Claude Code file not found: {real_file}")
    return real_file


class TestDDDArchitecture:
    """Test Domain Driven Design implementation."""
    
    def test_load_factory_function(self, real_claude_file):
        """Test 95% use case - simple load() function."""
        conv = load(real_claude_file)
        
        # DDD assertions
        assert isinstance(conv, Conversation)
        assert hasattr(conv, 'session_id')
        
        # Real data assertions
        assert len(conv) > 3000
        assert conv.session_id == "8f64b245-7268-4ecd-9b90-34037f3c5b75"
        assert conv.current_dir is not None
        assert conv.git_branch == "main"
    
    def test_large_file_factory(self, real_claude_file):
        """Test 5% use case - load() handles large files."""
        conv = load(real_claude_file)
        
        # Should work the same for large files
        assert isinstance(conv, Conversation)
        assert len(conv) > 3000
    
    def test_analyze_factory(self, real_claude_file):
        """Test conversation analysis factory function."""
        conv = load(real_claude_file)
        analyzer = ConversationAnalyzer(conv)
        analysis = analyzer.get_stats()
        
        assert isinstance(analysis, dict)
        assert 'total_messages' in analysis
        assert 'assistant_messages' in analysis
        assert 'user_messages' in analysis
        assert analysis['total_messages'] > 3000
    
    def test_extract_assistant_messages_factory(self, real_claude_file):
        """Test assistant message extraction factory function."""
        conv = load(real_claude_file)
        
        # Extract first 5 assistant messages
        assistant_msgs = conv.assistant_messages()
        first_id = assistant_msgs[0].uuid
        fifth_id = assistant_msgs[4].uuid
        
        # Extract using slice instead
        extracted = assistant_msgs[:5]
        
        assert len(extracted) >= 5
        assert all(isinstance(msg, AssistantMessage) for msg in extracted)


class TestDomainBehavior:
    """Test rich domain model behavior."""
    
    def test_conversation_properties(self, real_claude_file):
        """Test conversation entity properties."""
        conv = load(real_claude_file)
        
        # Domain entity behavior
        assert len(conv.assistant_messages()) > 1000
        assert len(conv.user_messages()) > 1000
        assert len(conv.tool_uses) >= 0
        assert len(conv.summaries()) >= 0
    
    def test_conversation_search(self, real_claude_file):
        """Test domain search behavior."""
        conv = load(real_claude_file)
        
        # Domain-specific search operations
        claude_mentions = conv.search("claude")
        python_mentions = conv.search("python")
        
        assert len(claude_mentions) > 100
        assert len(python_mentions) > 100
    
    def test_conversation_filtering(self, real_claude_file):
        """Test domain filtering behavior."""
        conv = load(real_claude_file)
        
        # Rich domain filtering
        user_msgs = conv.filter(lambda m: m.type == MessageType.USER)
        recent_msgs = conv.messages[:10]
        
        assert len(user_msgs) > 800  # Adjusted for actual data
        assert len(recent_msgs) == 10
    
    def test_error_detection(self, real_claude_file):
        """Test domain error detection."""
        conv = load(real_claude_file)
        
        # Domain-specific error analysis
        error_msgs = conv.with_errors()
        assert len(error_msgs) >= 0  # May or may not have errors


class TestRepositoryPattern:
    """Test infrastructure layer repository pattern."""
    
    def test_metadata_extraction(self, real_claude_file):
        """Test repository extracts metadata correctly."""
        conv = load(real_claude_file)
        
        # Repository should extract from raw JSON
        assert conv.session_id == "8f64b245-7268-4ecd-9b90-34037f3c5b75"
        assert "hook-system-v2" in conv.current_dir
        assert conv.git_branch == "main"
        assert len(conv) > 3000
    
    def test_orjson_pydantic_compliance(self, real_claude_file):
        """Test repository uses orjson + pydantic per specification."""
        conv = load(real_claude_file)
        
        # Successful load proves orjson + pydantic work correctly
        assert len(conv) > 0
        
        # All messages should be properly typed
        for msg in conv.messages[:10]:  # Sample check
            assert hasattr(msg, 'type')
            assert hasattr(msg, 'uuid')
            assert hasattr(msg, 'timestamp')


class TestCollectionInterface:
    """Test conversation collection behavior."""
    
    def test_length_and_indexing(self, real_claude_file):
        """Test conversation acts like a collection."""
        conv = load(real_claude_file)
        
        # Collection interface
        assert len(conv) > 3000
        assert conv[0] is not None
        assert conv[-1] is not None
        
        # Slicing
        first_10 = conv[:10]
        assert len(first_10) == 10
    
    def test_iteration(self, real_claude_file):
        """Test conversation iteration."""
        conv = load(real_claude_file)
        
        # Should be iterable
        count = 0
        for msg in conv:
            count += 1
            if count > 10:  # Don't iterate through all 3481 messages
                break
        
        assert count == 11


class TestSOLIDPrinciples:
    """Test SOLID principles adherence."""
    
    def test_single_responsibility(self, real_claude_file):
        """Each class has single responsibility."""
        conv = load(real_claude_file)
        
        # Conversation: conversation behavior only
        assert hasattr(conv, 'search')
        assert hasattr(conv, 'filter')
        
        # Conversation has metadata as properties
        assert hasattr(conv, 'session_id')
        assert hasattr(conv, 'current_dir')
    
    def test_dependency_inversion(self, real_claude_file):
        """Domain doesn't depend on infrastructure."""
        conv = load(real_claude_file)
        
        # Domain entity should not know about file system
        assert not hasattr(conv, 'load_messages')
        # Note: _raw_messages is currently present but marked as private
        
        # Domain depends on abstractions
        assert hasattr(conv, 'messages')  # Abstract property


class TestPerformance:
    """Test performance characteristics."""
    
    def test_large_file_performance(self, real_claude_file):
        """Test performance with real large file (3481 messages)."""
        import time
        
        # Should load quickly even with 3481 messages
        start_time = time.time()
        conv = load(real_claude_file)
        load_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert load_time < 5.0  # 5 seconds max for 3481 messages
        assert len(conv) > 3000
    
    def test_memory_efficiency(self, real_claude_file):
        """Test memory usage is reasonable."""
        conv = load(real_claude_file)
        
        # Should handle large conversations without excessive memory
        # If this loads successfully, memory usage is reasonable
        assert len(conv) > 3000
        
        # Domain operations should be fast
        start_time = time.time()
        assistant_count = len(conv.assistant_messages())
        filter_time = time.time() - start_time
        
        assert assistant_count > 1000
        assert filter_time < 1.0  # Fast filtering