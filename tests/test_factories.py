"""
Test factory utilities for reducing duplication.

SOLID: Single Responsibility - Each factory has one job
DRY: Eliminate test duplication
95/5: Using existing test libraries
"""

from pathlib import Path
from typing import Any, Dict, Optional


class TestDefaults:
    """Default test values to eliminate magic strings."""
    
    SESSION_ID = 'test-session-001'
    TRANSCRIPT_PATH = Path('/tmp/test-transcript.jsonl')
    PROJECT_PATH = Path('/tmp/test-project')
    USER_UUID = 'user-msg-001'
    ASSISTANT_UUID = 'asst-msg-001'
    TIMESTAMP = '2025-01-01T00:00:00.000Z'
    MODEL = 'claude-3-opus-20240229'
    
    @classmethod
    def create_hook_data(cls, **overrides) -> Dict[str, Any]:
        """Create hook data with defaults."""
        defaults = {
            'sessionId': cls.SESSION_ID,
            'transcriptPath': str(cls.TRANSCRIPT_PATH),
            'cwd': str(cls.PROJECT_PATH),
        }
        return {**defaults, **overrides}
    
    @classmethod
    def create_message_data(cls, message_type: str = 'user', **overrides) -> Dict[str, Any]:
        """Create message data with defaults."""
        defaults = {
            'type': message_type,
            'uuid': cls.USER_UUID if message_type == 'user' else cls.ASSISTANT_UUID,
            'timestamp': cls.TIMESTAMP,
            'sessionId': cls.SESSION_ID,
        }
        
        if message_type == 'assistant':
            defaults['model'] = cls.MODEL
            
        return {**defaults, **overrides}


class HookTestFactory:
    """Factory for creating hook test cases without duplication."""
    
    @staticmethod
    def create_tool_response_test(tool_name: str, sample_output: str):
        """Create a parameterized test for tool responses."""
        def test_function():
            from claude_parser.hooks.models import parseHookData
            
            response = TestDefaults.create_hook_data(
                hookEventName='PostToolUse',
                toolName=tool_name,
                toolResponse=sample_output
            )
            
            result = parseHookData(response)
            assert result.success, f"Failed to parse {tool_name} response"
            
            if result.success:
                data = result.data
                assert data.tool_name == tool_name
                assert isinstance(data.tool_response, str)
                assert data.tool_response == sample_output
                
        return test_function
    
    @staticmethod
    def create_type_guard_test(guard_function, valid_data, invalid_data):
        """Create a parameterized test for type guards."""
        def test_function():
            # Test valid data
            assert guard_function(valid_data) is True, "Guard should accept valid data"
            
            # Test invalid data
            assert guard_function(invalid_data) is False, "Guard should reject invalid data"
            
        return test_function


class MessageTestFactory:
    """Factory for creating message test cases."""
    
    @staticmethod
    def create_parsing_test(message_data: Dict[str, Any], expected_type: type):
        """Create a parameterized test for message parsing."""
        def test_function():
            from claude_parser.models.parser import parse_message
            
            message = parse_message(message_data)
            assert message is not None, "Failed to parse message"
            assert isinstance(message, expected_type), f"Expected {expected_type.__name__}"
            
            # Verify basic fields
            if 'uuid' in message_data:
                assert message.uuid == message_data['uuid']
            if 'timestamp' in message_data:
                assert str(message.timestamp) == message_data['timestamp']
                
        return test_function
    
    @staticmethod
    def create_validation_test(validator_function, valid_samples: list, invalid_samples: list):
        """Create a parameterized test for validators."""
        def test_function():
            # Test valid samples
            for sample in valid_samples:
                result = validator_function(sample)
                assert result is True, f"Should accept: {sample}"
            
            # Test invalid samples
            for sample in invalid_samples:
                result = validator_function(sample)
                assert result is False, f"Should reject: {sample}"
                
        return test_function


class ConversationTestFactory:
    """Factory for creating conversation test cases."""
    
    @staticmethod
    def create_filter_test(filter_type: str, expected_count: int):
        """Create a parameterized test for conversation filters."""
        def test_function(conversation):
            if filter_type == 'assistant':
                results = conversation.assistant_messages
            elif filter_type == 'user':
                results = conversation.user_messages
            elif filter_type == 'tool':
                results = conversation.tool_uses
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")
                
            assert len(results) == expected_count, f"Expected {expected_count} {filter_type} messages"
            
        return test_function
    
    @staticmethod  
    def create_search_test(query: str, case_sensitive: bool, expected_matches: int):
        """Create a parameterized test for search functionality."""
        def test_function(conversation):
            results = conversation.search(query, case_sensitive=case_sensitive)
            assert len(results) == expected_matches, f"Expected {expected_matches} matches for '{query}'"
            
            # Verify all results contain the query
            for result in results:
                if case_sensitive:
                    assert query in result.text_content
                else:
                    assert query.lower() in result.text_content.lower()
                    
        return test_function


# Sample tool outputs for consistent testing
TOOL_OUTPUTS = {
    'LS': '- /Users/ali/.claude/projects/\n  - file.md\n  - subdir/',
    'Grep': 'file.ts:10: const result = parseMessage(data)\nfile.ts:20: if (result.success)',
    'Read': '# README\n\nThis is the file content...\n\nMultiple lines of text.',
    'Bash': 'npm test\n\n✓ 23 tests passed\n✓ 0 tests failed\n\nTest suite completed.',
    'Edit': 'File updated successfully at: /path/to/file.py',
    'Write': 'File created successfully at: /path/to/new.py',
}

# Sample validation data for consistent testing  
VALID_HOOK_EVENTS = ['PreToolUse', 'PostToolUse', 'Stop', 'UserPromptSubmit']
INVALID_HOOK_EVENTS = ['InvalidEvent', 'ToolUse', 'Start', '']

# Export for use in tests
__all__ = [
    'TestDefaults',
    'HookTestFactory', 
    'MessageTestFactory',
    'ConversationTestFactory',
    'TOOL_OUTPUTS',
    'VALID_HOOK_EVENTS',
    'INVALID_HOOK_EVENTS',
]