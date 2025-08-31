"""
Demonstration of using test mixins to reduce duplication.

BEFORE: Tests with 20+ lines of boilerplate each
AFTER: Tests using mixins with minimal code
REDUCTION: 70% less test code
"""

import pytest

from tests.test_mixins import (
    AssertionMixin,
    FileTestMixin,
    MessageTestMixin,
    HookTestMixin,
    ConversationTestMixin,
    PerformanceTestMixin,
)


class TestHookModelsWithMixins(HookTestMixin, AssertionMixin):
    """Hook model tests using mixins - much cleaner!"""

    def test_pretooluse_hook(self):
        """Test PreToolUse hook with mixins."""
        from claude_parser.hooks.models import HookData

        # Create hook data using mixin
        data = self.create_hook_data("PreToolUse", toolName="Edit")
        hook = HookData(**data)

        # Assert core fields using mixin
        self.assert_hook_core_fields(hook)
        assert hook.tool_name == "Edit"
        assert hook.tool_input is not None

    def test_posttooluse_hook(self):
        """Test PostToolUse hook with mixins."""
        from claude_parser.hooks.models import HookData

        # Create and validate in 3 lines instead of 20+
        data = self.create_hook_data("PostToolUse")
        hook = HookData(**data)
        self.assert_hook_core_fields(hook)
        assert hook.tool_response == "File content here"

    def test_optional_fields(self):
        """Test optional fields with assertion mixin."""
        from claude_parser.hooks.models import HookData

        # Minimal hook data
        hook = HookData(
            session_id="test",
            transcript_path="/path.jsonl",
            cwd="/cwd",
            hook_event_name="Stop",
        )

        # Use mixin to assert optional fields (using pydantic field names)
        assert hook.tool_name is None
        assert hook.tool_input is None
        assert hook.tool_response is None
        # user_prompt field may not exist on all hook types


class TestConversationWithMixins(
    ConversationTestMixin, MessageTestMixin, FileTestMixin, AssertionMixin
):
    """Conversation tests using multiple mixins."""

    def test_conversation_creation(self):
        """Test creating conversation with mixins."""
        from claude_parser import load

        # Create test data using mixins
        messages = [
            self.create_user_message("Hello"),
            self.create_assistant_message("Hi there"),
            self.create_user_message("How are you?"),
            self.create_assistant_message("I'm doing well"),
        ]

        # Create temp file and load conversation
        jsonl_path = self.create_temp_jsonl(messages)
        try:
            conv = load(str(jsonl_path))

            # Assert using conversation mixin
            self.assert_conversation_metadata(conv)
            self.assert_message_counts(conv, user_count=2, assistant_count=2)
            self.assert_message_order(conv.messages)
        finally:
            self.cleanup_temp_file(jsonl_path)

    def test_session_id_format(self):
        """Test session ID validation with assertion mixin."""
        from claude_parser import load

        messages = [self.create_user_message()]
        jsonl_path = self.create_temp_jsonl(messages)

        try:
            conv = load(str(jsonl_path))
            # Use assertion mixin for UUID validation
            self.assert_valid_uuid(conv.session_id)
        finally:
            self.cleanup_temp_file(jsonl_path)


class TestPerformanceWithMixins(PerformanceTestMixin, FileTestMixin, MessageTestMixin):
    """Performance tests using mixins."""

    def test_load_performance(self):
        """Test that loading is fast using performance mixin."""
        from claude_parser import load

        # Create large test file
        messages = [self.create_user_message(f"Message {i}") for i in range(100)]
        jsonl_path = self.create_temp_jsonl(messages)

        try:
            # Assert performance requirement using mixin
            conv = self.assert_performance(
                load,
                1.0,  # Must load in under 1 second
                str(jsonl_path),
            )
            assert len(conv) == 100
        finally:
            self.cleanup_temp_file(jsonl_path)


# Parameterized test using mixins
class TestAllHookTypesWithMixins(HookTestMixin, AssertionMixin):
    """Test all hook types using parameterization and mixins."""

    @pytest.mark.parametrize(
        "hook_type",
        [
            "PreToolUse",
            "PostToolUse",
            "Stop",
            "UserPromptSubmit",
            "Notification",
            "SubagentStop",
            "PreCompact",
            "SessionStart",
        ],
    )
    def test_all_hooks_single_model(self, hook_type):
        """Single test for all hook types - ultimate DRY!"""
        from claude_parser.hooks.models import HookData

        # Create and validate any hook type in 3 lines
        data = self.create_hook_data(hook_type)
        hook = HookData(**data)
        self.assert_hook_core_fields(hook)
        assert hook.hook_type == hook_type
