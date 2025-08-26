"""Tests for exit helper functions - TDD approach, tests written FIRST.

Success criteria:
- exit_success() exits with code 0
- exit_block() exits with code 2
- exit_error() exits with code 1
- Correct stdout/stderr routing
- Functions are simple (≤ 3 lines each)
"""


import pytest


def test_exit_success_no_message(capsys):
    """exit_success() with no message exits cleanly."""
    from claude_parser.hooks import exit_success

    with pytest.raises(SystemExit) as exc:
        exit_success()

    assert exc.value.code == 0

    # Should output {"continue": true} JSON
    captured = capsys.readouterr()
    assert captured.out == '{"continue":true}'
    assert captured.err == ""


def test_exit_success_with_message(capsys):
    """exit_success() with message writes to stdout."""
    from claude_parser.hooks import exit_success

    with pytest.raises(SystemExit) as exc:
        exit_success("Operation completed successfully")

    assert exc.value.code == 0

    # Message goes to stdout as JSON
    captured = capsys.readouterr()
    assert (
        captured.out == '{"continue":true,"message":"Operation completed successfully"}'
    )
    assert captured.err == ""


def test_exit_block_with_reason(capsys):
    """exit_block() requires reason and exits with code 2."""
    from claude_parser.hooks import exit_block

    with pytest.raises(SystemExit) as exc:
        exit_block("Security violation: attempting to modify system files")

    assert exc.value.code == 2

    # Reason goes to stderr
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Security violation: attempting to modify system files\n"


def test_exit_error_with_message(capsys):
    """exit_error() exits with code 1 and message to stderr."""
    from claude_parser.hooks import exit_error

    with pytest.raises(SystemExit) as exc:
        exit_error("Warning: deprecated function used")

    assert exc.value.code == 1

    # Message goes to stderr
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Warning: deprecated function used\n"


def test_exit_functions_are_simple():
    """Exit functions follow Single Responsibility Principle."""
    import inspect

    from claude_parser.hooks import exit_block, exit_error, exit_success

    # Each function should be very simple
    for func in [exit_success, exit_block, exit_error]:
        source = inspect.getsource(func)

        # Remove docstring and comments for line count
        lines = [
            line
            for line in source.split("\n")
            if line.strip()
            and not line.strip().startswith("#")
            and not line.strip().startswith('"""')
            and '"""' not in line
        ]

        # Should be very short (function def + 1-3 lines of code)
        assert len(lines) <= 5, f"{func.__name__} is too complex"

        # Should not have complex logic
        assert source.count("if") <= 1  # At most one if for optional param
        assert source.count("for") == 0  # No loops
        assert source.count("while") == 0  # No loops
        assert source.count("try") == 0  # No error handling needed


def test_exit_success_empty_string(capsys):
    """exit_success() with empty string behaves like no message."""
    from claude_parser.hooks import exit_success

    with pytest.raises(SystemExit) as exc:
        exit_success("")

    assert exc.value.code == 0

    # Empty string should output continue JSON (same as no message)
    captured = capsys.readouterr()
    assert captured.out == '{"continue":true}'
    assert captured.err == ""


def test_exit_functions_type_hints():
    """Exit functions have proper type hints."""
    import inspect
    from typing import NoReturn

    from claude_parser.hooks import exit_block, exit_error, exit_success

    # Check type hints
    for func in [exit_success, exit_block, exit_error]:
        sig = inspect.signature(func)

        # Should return NoReturn (since they call sys.exit)
        assert (
            sig.return_annotation == NoReturn or sig.return_annotation == "NoReturn"
        ), f"{func.__name__} should have NoReturn type hint"


def test_exit_block_unicode_reason(capsys):
    """exit_block() handles unicode in reason."""
    from claude_parser.hooks import exit_block

    with pytest.raises(SystemExit) as exc:
        exit_block("错误: 不允许的操作")  # Chinese characters

    assert exc.value.code == 2

    captured = capsys.readouterr()
    assert "错误: 不允许的操作" in captured.err


def test_exit_success_multiline_message(capsys):
    """exit_success() handles multiline messages."""
    from claude_parser.hooks import exit_success

    message = "Line 1\nLine 2\nLine 3"

    with pytest.raises(SystemExit) as exc:
        exit_success(message)

    assert exc.value.code == 0

    captured = capsys.readouterr()
    import orjson

    output = orjson.loads(captured.out)
    assert output["continue"] == True
    assert output["message"] == "Line 1\nLine 2\nLine 3"


def test_exit_functions_are_exported():
    """Exit functions are properly exported from hooks module."""
    from claude_parser import hooks

    # Should be accessible from main hooks module
    assert hasattr(hooks, "exit_success")
    assert hasattr(hooks, "exit_block")
    assert hasattr(hooks, "exit_error")

    # Should be callable
    assert callable(hooks.exit_success)
    assert callable(hooks.exit_block)
    assert callable(hooks.exit_error)
