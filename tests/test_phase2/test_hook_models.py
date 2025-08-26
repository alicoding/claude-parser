"""Tests for HookData model - TDD approach, tests written FIRST.

Success criteria:
- Single HookData model handles ALL 8 hook types (DRY)
- Uses pydantic BaseModel with field aliases (no manual parsing)
- All fields are Optional except core 3 (session_id, transcript_path, hook_event_name)
- NO isinstance checks needed by users (Liskov Substitution)
- NO separate classes per hook type (violates DRY)
"""

import pytest


def test_single_model_all_hooks(hook_sample, all_hook_types):
    """Single HookData model handles ALL 8 hook types (DRY principle)."""
    from claude_parser.hooks.models import HookData

    # Test that one model works for all hook types
    for hook_type in all_hook_types:
        data = HookData(**hook_sample(hook_type))

        # Core fields always present
        assert data.hook_event_name == hook_type
        assert data.session_id == "abc123"
        assert data.transcript_path == "/Users/test/.claude/projects/test/session.jsonl"
        assert data.cwd == "/Users/test/project"

        # Convenience property
        assert data.hook_type == hook_type


def test_optional_fields_are_none():
    """Optional fields default to None when not provided."""
    from claude_parser.hooks.models import HookData

    # Create with minimal required fields
    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse",
    )

    # Tool-specific fields should be None
    assert data.tool_name is None
    assert data.tool_input is None
    assert data.tool_response is None

    # Other optional fields
    assert data.prompt is None
    assert data.message is None
    assert data.stop_hook_active is None
    assert data.trigger is None
    assert data.custom_instructions is None
    assert data.source is None


def test_optional_fields_when_provided():
    """Optional fields work correctly when provided."""
    from claude_parser.hooks.models import HookData

    # Create with optional fields
    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse",
        tool_name="Write",
        tool_input={"file_path": "/test.txt", "content": "hello"},
    )

    assert data.tool_name == "Write"
    assert data.tool_input["file_path"] == "/test.txt"
    assert data.tool_input["content"] == "hello"


def test_model_is_immutable():
    """Models are frozen (immutable) following DDD value object pattern."""
    from pydantic import ValidationError

    from claude_parser.hooks.models import HookData

    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse",
    )

    # Should not be able to modify after creation
    # Pydantic 2.0 raises ValidationError for frozen models
    with pytest.raises((AttributeError, TypeError, ValidationError)):
        data.session_id = "changed"

    with pytest.raises((AttributeError, TypeError, ValidationError)):
        data.hook_event_name = "different"


def test_load_conversation_integration(real_transcript):
    """HookData can load conversation using Phase 1 parser."""
    from claude_parser.hooks.models import HookData

    data = HookData(
        session_id="test",
        transcript_path=real_transcript,
        cwd="/test",
        hook_event_name="PreToolUse",
    )

    # Should be able to load the conversation
    conv = data.load_conversation()
    assert conv is not None
    assert len(conv) > 0


def test_hook_type_property():
    """hook_type property provides convenience alias for hook_event_name."""
    from claude_parser.hooks.models import HookData

    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/test",
        hook_event_name="PreToolUse",
    )

    # Property should return the hook_event_name
    assert data.hook_type == "PreToolUse"
    assert data.hook_type == data.hook_event_name


def test_all_hook_specific_fields():
    """Test hook-specific fields for each hook type."""
    from claude_parser.hooks.models import HookData

    # PreToolUse - has tool fields
    pre_tool = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="PreToolUse",
        tool_name="Write",
        tool_input={"file_path": "/test.txt"},
    )
    assert pre_tool.tool_name == "Write"
    assert pre_tool.tool_input["file_path"] == "/test.txt"

    # PostToolUse - has tool response
    post_tool = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="PostToolUse",
        tool_name="Bash",
        tool_response={"success": True, "output": "done"},
    )
    assert post_tool.tool_response["success"] is True

    # UserPromptSubmit - has prompt
    prompt = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="UserPromptSubmit",
        prompt="Write a function",
    )
    assert prompt.prompt == "Write a function"

    # Notification - has message
    notif = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="Notification",
        message="Claude needs permission",
    )
    assert notif.message == "Claude needs permission"

    # Stop - has stop_hook_active
    stop = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="Stop",
        stop_hook_active=False,
    )
    assert stop.stop_hook_active is False

    # SessionStart - has source
    start = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="SessionStart",
        source="startup",
    )
    assert start.source == "startup"

    # PreCompact - has trigger and custom_instructions
    compact = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="PreCompact",
        trigger="manual",
        custom_instructions="Keep errors",
    )
    assert compact.trigger == "manual"
    assert compact.custom_instructions == "Keep errors"


def test_extra_fields_allowed():
    """Model allows extra fields for forward compatibility."""
    from claude_parser.hooks.models import HookData

    # Should accept unknown fields without error
    data = HookData(
        session_id="test",
        transcript_path="/test.jsonl",
        cwd="/test",
        hook_event_name="PreToolUse",
        future_field="some value",  # Unknown field
        another_new_field=123,  # Another unknown field
    )

    # Core fields still work
    assert data.session_id == "test"
    assert data.hook_event_name == "PreToolUse"


def test_validation_errors():
    """Test that required fields are validated."""
    from pydantic import ValidationError

    from claude_parser.hooks.models import HookData

    # Missing required field should raise error
    with pytest.raises(ValidationError) as exc:
        HookData(
            session_id="test",
            transcript_path="/test.jsonl",
            # Missing cwd and hook_event_name
        )

    # Error should mention missing fields
    error = str(exc.value)
    assert "cwd" in error.lower() or "required" in error.lower()

    # Empty required fields should also fail
    with pytest.raises(ValidationError) as exc2:
        HookData(
            session_id="",  # Empty string should fail min_length validation
            transcript_path="/test.jsonl",
            cwd="/test",
            hook_event_name="PreToolUse",
        )

    # Check that the error is about the empty string
    error2 = str(exc2.value)
    assert (
        "at least 1 character" in error2
        or "min_length" in error2.lower()
        or "string_too_short" in error2.lower()
    )
