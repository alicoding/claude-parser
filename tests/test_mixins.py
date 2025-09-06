"""
Test mixins for reducing duplication.

SOLID: Single Responsibility - Each mixin has one testing concern.
DRY: Eliminate common test patterns.
95/5: Reusable test components.
"""

import tempfile
from pathlib import Path
from typing import Any, Dict, List
import orjson

from tests.constants import TestDefaults


class AssertionMixin:
    """Common assertion patterns."""

    def assert_valid_uuid(self, uuid: str):
        """Assert value is a valid UUID format."""
        assert isinstance(uuid, str)
        assert len(uuid) == 36
        assert uuid.count("-") == 4

    def assert_timestamp_format(self, timestamp: str):
        """Assert timestamp follows expected format."""
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO format
        assert timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp[-6:]

    def assert_required_fields(self, obj: Any, fields: List[str]):
        """Assert object has all required fields."""
        for field in fields:
            assert hasattr(obj, field), f"Missing required field: {field}"
            assert getattr(obj, field) is not None, f"Required field is None: {field}"

    def assert_optional_fields_none(self, obj: Any, fields: List[str]):
        """Assert optional fields are None when not provided."""
        for field in fields:
            assert getattr(obj, field) is None, f"Optional field should be None: {field}"

    def assert_field_type(self, obj: Any, field: str, expected_type: type):
        """Assert field has expected type."""
        value = getattr(obj, field)
        assert isinstance(value, expected_type), (
            f"Field {field} should be {expected_type.__name__}, got {type(value).__name__}"
        )


class FileTestMixin:
    """Mixin for tests involving temporary files."""

    def create_temp_jsonl(self, messages: List[Dict]) -> Path:
        """Create a temporary JSONL file with messages."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.jsonl', delete=False) as f:
            for msg in messages:
                f.write(orjson.dumps(msg))
                f.write(b'\n')
            return Path(f.name)

    def create_temp_directory(self) -> Path:
        """Create a temporary directory."""
        return Path(tempfile.mkdtemp())

    def cleanup_temp_file(self, path: Path):
        """Clean up temporary file."""
        if path and path.exists():
            path.unlink()

    def cleanup_temp_directory(self, path: Path):
        """Clean up temporary directory and contents."""
        if path and path.exists():
            import shutil
            shutil.rmtree(path)


class MessageTestMixin:
    """Mixin for message-related tests."""

    def create_user_message(self, content: str = "test", **overrides) -> Dict:
        """Create a user message with defaults."""
        defaults = {
            'type': 'user',
            'uuid': TestDefaults.USER_UUID,
            'timestamp': TestDefaults.TIMESTAMP,
            'sessionId': TestDefaults.SESSION_ID,
            'message': {'role': 'user', 'content': [{'type': 'text', 'text': content}]}
        }
        return {**defaults, **overrides}

    def create_assistant_message(self, content: str = "response", **overrides) -> Dict:
        """Create an assistant message with defaults."""
        defaults = {
            'type': 'assistant',
            'uuid': TestDefaults.ASSISTANT_UUID,
            'timestamp': TestDefaults.TIMESTAMP,
            'sessionId': TestDefaults.SESSION_ID,
            'model': TestDefaults.MODEL,
            'message': {
                'role': 'assistant',
                'content': [{'type': 'text', 'text': content}]
            }
        }
        return {**defaults, **overrides}

    def create_summary_message(self, content: str = "summary", **overrides) -> Dict:
        """Create a summary message with defaults."""
        defaults = {
            'type': 'summary',
            'uuid': 'summary-001',
            'timestamp': TestDefaults.TIMESTAMP,
            'sessionId': TestDefaults.SESSION_ID,
            'message': {'summary': content}
        }
        return {**defaults, **overrides}


class HookTestMixin:
    """Mixin for hook-related tests."""

    def create_hook_data(self, hook_type: str, **overrides) -> Dict:
        """Create hook data for any hook type."""
        base = {
            'sessionId': TestDefaults.SESSION_ID,
            'transcriptPath': TestDefaults.TRANSCRIPT_PATH,
            'cwd': TestDefaults.PROJECT_PATH,
            'hookEventName': hook_type
        }

        # Add type-specific fields
        if hook_type == "PreToolUse":
            base.update({
                'toolName': 'Read',
                'toolInput': {'file': 'test.py'}
            })
        elif hook_type == "PostToolUse":
            base.update({
                'toolName': 'Read',
                'toolResponse': 'File content here'
            })
        elif hook_type == "UserPromptSubmit":
            base.update({
                'userPrompt': 'test prompt',
                'gitBranch': 'main'
            })

        return {**base, **overrides}

    def assert_hook_core_fields(self, hook_data):
        """Assert hook data has required core fields."""
        assert hook_data.session_id is not None
        assert hook_data.transcript_path is not None
        assert hook_data.hook_event_name is not None
        assert hook_data.cwd is not None


class ConversationTestMixin:
    """Mixin for conversation-related tests."""

    def assert_conversation_metadata(self, conversation):
        """Assert conversation has valid metadata."""
        assert conversation.metadata is not None
        if conversation.session_id:
            self.assert_valid_uuid(conversation.session_id)
        assert hasattr(conversation, 'messages')
        assert hasattr(conversation, 'assistant_messages')
        assert hasattr(conversation, 'user_messages')

    def assert_message_counts(self, conversation, user_count: int, assistant_count: int):
        """Assert expected message counts."""
        assert len(conversation.user_messages) == user_count
        assert len(conversation.assistant_messages) == assistant_count

    def assert_message_order(self, messages: List):
        """Assert messages are in chronological order."""
        if len(messages) <= 1:
            return

        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            if hasattr(prev_msg, 'timestamp') and hasattr(curr_msg, 'timestamp'):
                assert prev_msg.timestamp <= curr_msg.timestamp, (
                    "Messages not in chronological order"
                )


class PerformanceTestMixin:
    """Mixin for performance testing."""

    def measure_time(self, func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        return result, elapsed

    def assert_performance(self, func, max_seconds: float, *args, **kwargs):
        """Assert function completes within time limit."""
        result, elapsed = self.measure_time(func, *args, **kwargs)
        assert elapsed < max_seconds, (
            f"Performance requirement failed: {elapsed:.3f}s > {max_seconds}s"
        )
        return result


# Export for use in tests
__all__ = [
    'AssertionMixin',
    'FileTestMixin',
    'MessageTestMixin',
    'HookTestMixin',
    'ConversationTestMixin',
    'PerformanceTestMixin',
]
