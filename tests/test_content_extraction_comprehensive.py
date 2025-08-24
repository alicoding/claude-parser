"""
TDD Tests for comprehensive content extraction.
These tests should FAIL initially, then pass after fixing the implementation.
"""

import pytest
from pathlib import Path
from claude_parser import load


class TestContentExtractionConsistency:
    """Test that all message types extract content consistently."""
    
    def test_nested_list_content_extraction(self, tmp_path):
        """
        TDD: Test nested list content extraction (user/assistant messages).
        This should FAIL initially if text_content extraction is inconsistent.
        """
        file = tmp_path / "nested_content.jsonl"
        
        # Real format from Claude Code JSONL
        nested_user = '{"type": "user", "sessionId": "session-123", "message": {"role": "user", "content": [{"type": "text", "text": "Hello Claude, can you help me?"}]}}'
        nested_assistant = '{"type": "assistant", "sessionId": "session-123", "message": {"role": "assistant", "content": [{"type": "text", "text": "I can help you with that."}, {"type": "tool_use", "id": "tool-123", "name": "Bash", "input": {"command": "ls"}}]}}'
        
        file.write_text(f"{nested_user}\n{nested_assistant}")
        
        conv = load(file)
        
        # This should FAIL initially - text content extraction may be inconsistent
        user_msg = conv.user_messages[0]
        assert user_msg.text_content == "Hello Claude, can you help me?", f"Expected user text, got: {user_msg.text_content!r}"
        
        assistant_msg = conv.assistant_messages()()[0] 
        assert assistant_msg.text_content == "I can help you with that.", f"Expected assistant text, got: {assistant_msg.text_content!r}"
    
    def test_direct_string_content_extraction(self, tmp_path):
        """
        TDD: Test direct string content extraction (system messages).
        Should FAIL if system message content extraction is broken.
        """
        file = tmp_path / "direct_content.jsonl"
        
        # Real system message format
        system_msg = '{"type": "system", "sessionId": "session-123", "content": "Running PostToolUse:Bash...", "isMeta": false, "timestamp": "2025-08-19T19:19:16.364Z"}'
        
        file.write_text(system_msg)
        
        conv = load(file)
        
        # Should extract direct content string
        system_messages = [m for m in conv.messages if hasattr(m, 'content') and m.type.value == 'system']
        assert len(system_messages) > 0, "Should find system message"
        
        sys_msg = system_messages[0]
        assert sys_msg.text_content == "Running PostToolUse:Bash...", f"Expected system content, got: {sys_msg.text_content!r}"
    
    def test_summary_content_extraction(self, tmp_path):
        """
        TDD: Test summary content extraction (summary field).
        Should FAIL if summary text_content extraction is inconsistent.
        """
        file = tmp_path / "summary_content.jsonl"
        
        # Real summary format
        summary_msg = '{"type": "summary", "summary": "Redis Migration Roadmap: Systematic Platform Overhaul", "leafUuid": "uuid-123"}'
        
        file.write_text(summary_msg)
        
        conv = load(file)
        
        # Should extract summary field as text content
        assert len(conv.summaries()) > 0, "Should find summary message"
        
        summary = conv.summaries[0]
        assert summary.text_content == "Redis Migration Roadmap: Systematic Platform Overhaul", f"Expected summary text, got: {summary.text_content!r}"
    
    def test_mixed_content_types_search_consistency(self, tmp_path):
        """
        TDD: Test that search works across all content types.
        Should FAIL if search doesn't work consistently across message types.
        """
        file = tmp_path / "mixed_search.jsonl"
        
        messages = [
            '{"type": "user", "message": {"content": [{"type": "text", "text": "I need help with Redis migration"}]}}',
            '{"type": "assistant", "message": {"content": [{"type": "text", "text": "Redis migration requires careful planning"}]}}',
            '{"type": "system", "content": "Redis connection established"}',
            '{"type": "summary", "summary": "Redis Migration Progress: Rapid Success"}'
        ]
        
        file.write_text('\n'.join(messages))
        
        conv = load(file)
        
        # Search should find "Redis" in ALL message types
        redis_messages = conv.search("Redis", case_sensitive=False)
        
        # This should FAIL initially if content extraction is inconsistent
        assert len(redis_messages) == 4, f"Should find 'Redis' in all 4 messages, found in {len(redis_messages)}"
        
        # Verify each message type is found
        types_found = {msg.type.value for msg in redis_messages}
        expected_types = {"user", "assistant", "system", "summary"}
        assert types_found == expected_types, f"Missing types in search: {expected_types - types_found}"
    
    def test_empty_content_handling(self, tmp_path):
        """
        TDD: Test consistent handling of empty/missing content.
        Should FAIL if empty content handling is inconsistent.
        """
        file = tmp_path / "empty_content.jsonl"
        
        messages = [
            '{"type": "user", "message": {"content": []}}',  # Empty list
            '{"type": "assistant", "message": {"content": [{"type": "text", "text": ""}]}}',  # Empty text
            '{"type": "system", "content": ""}',  # Empty string
            '{"type": "summary", "summary": ""}',  # Empty summary
        ]
        
        file.write_text('\n'.join(messages))
        
        conv = load(file)
        
        # All should have empty text_content, not None or crash
        for msg in conv.messages:
            assert hasattr(msg, 'text_content'), f"Message {msg.type} missing text_content property"
            assert msg.text_content == "", f"Message {msg.type} should have empty string, got: {msg.text_content!r}"


class TestRealWorldContentExtraction:
    """Test with real JSONL file to ensure content extraction works."""
    
    def test_real_jsonl_content_extraction(self):
        """
        TDD: Test that real JSONL content extraction is consistent.
        Should FAIL initially if extraction doesn't work across all types.
        """
        real_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/2f283580-c24a-40af-8129-1be80c07b965.jsonl"
        
        if not Path(real_file).exists():
            pytest.skip("Real JSONL file not available")
        
        conv = load(real_file)
        
        # Get samples of each message type
        user_sample = next((m for m in conv.user_messages if hasattr(m, 'text_content')), None)
        assistant_sample = next((m for m in conv.assistant_messages if hasattr(m, 'text_content')), None) 
        system_sample = next((m for m in conv.messages if hasattr(m, 'type') and m.type.value == 'system'), None)
        summary_sample = next((m for m in conv.summaries if hasattr(m, 'text_content')), None)
        
        # All should have accessible text_content
        if user_sample:
            assert isinstance(user_sample.text_content, str), f"User text_content should be string, got {type(user_sample.text_content)}"
        
        if assistant_sample:
            assert isinstance(assistant_sample.text_content, str), f"Assistant text_content should be string, got {type(assistant_sample.text_content)}"
        
        if system_sample:
            assert isinstance(system_sample.text_content, str), f"System text_content should be string, got {type(system_sample.text_content)}"
        
        if summary_sample:
            assert isinstance(summary_sample.text_content, str), f"Summary text_content should be string, got {type(summary_sample.text_content)}"
        
        # Test search works across all types  
        search_results = conv.search("python", case_sensitive=False)
        
        # Should find results if the word exists in the file
        if search_results:
            result_types = {msg.type.value for msg in search_results}
            print(f"✅ Found 'python' in message types: {result_types}")
        
        print(f"✅ Content extraction tested on {len(conv)} messages")