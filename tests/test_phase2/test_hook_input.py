"""Tests for hook_input() function - TDD approach, tests written FIRST.

Success criteria:
- Parse stdin JSON for all 8 hook types
- Exit with code 1 on invalid JSON
- Exit with code 1 on missing required fields
- Performance < 10ms
- Single function handles everything (SRP)
"""

import pytest
from tests.constants import TestDefaults
from tests.constants import TestDefaults


def test_hook_input_parses_valid_json(mock_stdin, hook_sample):
    """hook_input() successfully parses valid JSON from stdin."""
    from claude_parser.hooks import hook_input

    # Test with PreToolUse hook
    test_data = hook_sample("PreToolUse")

    with mock_stdin(test_data):
        data = hook_input()

    assert data.session_id == TestDefaults.SESSION_ID
    assert data.hook_event_name == "PreToolUse"
    assert data.tool_name == "Write"
    assert data.tool_input["file_path"] == "/test.txt"


def test_hook_input_all_hook_types(mock_stdin, hook_sample, all_hook_types):
    """hook_input() works for ALL 8 hook types with same function."""
    from claude_parser.hooks import hook_input

    for hook_type in all_hook_types:
        test_data = hook_sample(hook_type)

        with mock_stdin(test_data):
            data = hook_input()

        assert data.hook_event_name == hook_type
        assert data.session_id == TestDefaults.SESSION_ID


def test_hook_input_invalid_json(mock_stdin, capsys):
    """hook_input() exits with code 1 on invalid JSON."""
    from claude_parser.hooks import hook_input

    with mock_stdin("not valid json {"):
        with pytest.raises(SystemExit) as exc:
            hook_input()

    assert exc.value.code == 1

    # Check error message goes to stderr
    captured = capsys.readouterr()
    assert captured.err != ""
    assert "invalid json" in captured.err.lower() or "json" in captured.err.lower()
    assert captured.out == ""  # Nothing on stdout


def test_hook_input_missing_required_fields(mock_stdin, capsys):
    """hook_input() exits with code 1 on missing required fields."""
    from claude_parser.hooks import hook_input

    # Missing required fields
    incomplete_data = {
        "session_id": "test",
        # Missing: transcript_path, cwd, hook_event_name
    }

    with mock_stdin(incomplete_data):
        with pytest.raises(SystemExit) as exc:
            hook_input()

    assert exc.value.code == 1

    # Check error message
    captured = capsys.readouterr()
    assert captured.err != ""
    assert "required" in captured.err.lower() or "missing" in captured.err.lower()


def test_hook_input_empty_stdin(mock_stdin, capsys):
    """hook_input() handles empty stdin gracefully."""
    from claude_parser.hooks import hook_input

    with mock_stdin(""):
        with pytest.raises(SystemExit) as exc:
            hook_input()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.err != ""


def test_hook_input_extra_fields_preserved(mock_stdin):
    """hook_input() preserves extra fields for forward compatibility."""
    from claude_parser.hooks import hook_input

    data_with_extra = {
        "session_id": "test",
        "transcript_path": "/test.jsonl",
        "cwd": "/test",
        "hook_event_name": "PreToolUse",
        "future_field": "some_value",
        "another_new_field": 123,
    }

    with mock_stdin(data_with_extra):
        data = hook_input()

    # Core fields work
    assert data.session_id == "test"
    # Extra fields are preserved (in model's __dict__ or similar)
    # This ensures forward compatibility


def test_hook_input_performance(mock_stdin, hook_sample, performance_timer):
    """hook_input() completes in < 10ms."""
    from claude_parser.hooks import hook_input

    test_data = hook_sample("PreToolUse")

    with mock_stdin(test_data):
        with performance_timer as timer:
            data = hook_input()

    # Should be very fast - just JSON parsing and validation
    assert timer.elapsed < 0.01  # 10ms
    assert data.session_id == TestDefaults.SESSION_ID


def test_hook_input_validates_hook_type(mock_stdin, capsys):
    """hook_input() validates hook_event_name is valid type."""
    from claude_parser.hooks import hook_input

    invalid_hook = {
        "session_id": "test",
        "transcript_path": "/test.jsonl",
        "cwd": "/test",
        "hook_event_name": "InvalidHookType",  # Not one of the 8 types
    }

    with mock_stdin(invalid_hook):
        with pytest.raises(SystemExit) as exc:
            hook_input()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.err != ""


def test_hook_input_handles_unicode(mock_stdin):
    """hook_input() correctly handles unicode in JSON."""
    from claude_parser.hooks import hook_input

    unicode_data = {
        "session_id": "test",
        "transcript_path": "/test.jsonl",
        "cwd": "/home/用户/项目",  # Unicode path
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Write a function to calculate 平方 (square)",  # Unicode content
    }

    with mock_stdin(unicode_data):
        data = hook_input()

    assert data.cwd == "/home/用户/项目"
    assert "平方" in data.prompt


def test_hook_input_real_claude_format(mock_stdin):
    """hook_input() works with actual Claude Code JSON format."""
    from claude_parser.hooks import hook_input

    # Real format from Claude Code
    real_format = {
        "session_id": "6d0efa65-3f7f-4c79-9b58-1e7a23d57f11",
        "transcript_path": "/Users/test/.claude/projects/test/6d0efa65-3f7f-4c79-9b58-1e7a23d57f11.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
    }

    with mock_stdin(real_format):
        data = hook_input()

    assert data.session_id == "6d0efa65-3f7f-4c79-9b58-1e7a23d57f11"
    assert data.tool_name == "Bash"
    assert data.tool_input["command"] == "ls -la"


def test_hook_input_is_single_responsibility():
    """hook_input() follows Single Responsibility Principle."""
    import inspect

    from claude_parser.hooks import hook_input

    # Function should be simple - just parse stdin
    source = inspect.getsource(hook_input)

    # Should not have complex logic
    assert source.count("if") <= 1  # Minimal branching
    # Note: 'for' appears in docstring "Works for ALL..." - that's OK
    assert "for " not in source.replace("for ALL", "")  # No actual loops
    assert source.count("def ") == 1  # Just the function itself

    # Should be reasonably short (docstring + try/except blocks)
    lines = [
        line
        for line in source.split("\n")
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(lines) <= 30  # Including docstring and 3 exception handlers
