"""
Test constants to eliminate magic strings.

This module provides default values for tests to avoid duplication
and magic strings throughout the test suite.
"""


class TestDefaults:
    """Default values for test data."""
    
    # Session and identification
    SESSION_ID = '12345678-1234-5678-1234-567812345678'  # Valid UUID format
    USER_UUID = 'user-msg-001'
    ASSISTANT_UUID = 'asst-msg-001'
    
    # Paths
    TRANSCRIPT_PATH = '/tmp/test-transcript.jsonl'
    PROJECT_PATH = '/tmp/test-project'
    
    # Timestamps and metadata
    TIMESTAMP = '2025-01-01T00:00:00.000Z'
    MODEL = 'claude-3-opus-20240229'
    
    # Git metadata
    GIT_BRANCH = 'main'
    
    # Common test values
    PARENT_UUID = 'parent-msg-001'
    LEAF_UUID = 'leaf-msg-001'
    
    @classmethod
    def create_basic_message(cls, message_type: str = 'user', **overrides):
        """Create a basic message with defaults."""
        defaults = {
            'type': message_type,
            'uuid': cls.USER_UUID if message_type == 'user' else cls.ASSISTANT_UUID,
            'sessionId': cls.SESSION_ID,
            'timestamp': cls.TIMESTAMP,
        }
        defaults.update(overrides)
        return defaults