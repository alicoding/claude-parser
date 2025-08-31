"""Test infrastructure for Phase 2 hooks testing.

Following TDD approach - writing test fixtures FIRST before implementation.
"""

import sys
from io import StringIO
from pathlib import Path
from typing import Any, Dict, Optional

import orjson
import pytest
from tests.constants import TestDefaults

# Real hook JSON samples from Claude Code documentation
HOOK_SAMPLES = {
    "PreToolUse": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/test.txt", "content": "test content"},
    },
    "PostToolUse": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "ls -la"},
        "tool_response": {"output": "file1.txt\nfile2.txt", "success": True},
    },
    "UserPromptSubmit": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "UserPromptSubmit",
        "prompt": "Write a function to calculate factorial",
    },
    "Stop": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "Stop",
        "stop_hook_active": False,
    },
    "SubagentStop": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "SubagentStop",
        "stop_hook_active": False,
    },
    "Notification": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "Notification",
        "message": "Claude needs your permission to use Bash",
    },
    "SessionStart": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "SessionStart",
        "source": "startup",
    },
    "PreCompact": {
        "session_id": TestDefaults.SESSION_ID,
        "transcript_path": "/Users/test/.claude/projects/test/session.jsonl",
        "cwd": "/Users/test/project",
        "hook_event_name": "PreCompact",
        "trigger": "manual",
        "custom_instructions": "",
    },
}


@pytest.fixture
def mock_stdin():
    """Mock stdin with JSON data for testing hook input.

    This simulates how Claude Code sends JSON to hook scripts via stdin.
    """
    from contextlib import contextmanager

    @contextmanager
    def _mock(data):
        """Set up stdin with the provided data.

        Args:
            data: Dict to convert to JSON, or raw string
        """
        if isinstance(data, dict):
            json_str = orjson.dumps(data).decode()
        else:
            json_str = data

        old_stdin = sys.stdin
        sys.stdin = StringIO(json_str)
        try:
            yield sys.stdin
        finally:
            sys.stdin = old_stdin

    return _mock


@pytest.fixture
def hook_sample():
    """Get hook sample data by type.

    Returns a function that retrieves sample data for a specific hook type.
    """

    def _get(hook_type: str) -> Dict[str, Any]:
        """Get sample data for a hook type.

        Args:
            hook_type: One of the 8 Claude hook types

        Returns:
            Copy of the sample data
        """
        if hook_type not in HOOK_SAMPLES:
            raise ValueError(f"Unknown hook type: {hook_type}")
        return HOOK_SAMPLES[hook_type].copy()

    return _get


@pytest.fixture
def all_hook_types():
    """Get list of all hook types for parametrized tests."""
    return list(HOOK_SAMPLES.keys())


@pytest.fixture
def real_transcript(tmp_path):
    """Create or use a real JSONL transcript file.

    Checks for actual transcript from hook-system-v2, otherwise creates test file.
    """
    # Try to use real file if available
    real_path = Path("/path/to/test/data")
    if real_path.exists():
        return str(real_path)

    # Create minimal test transcript
    test_file = tmp_path / "test_transcript.jsonl"
    test_data = [
        {"type": "user", "message": {"content": "test"}},
        {"type": "assistant", "message": {"content": "response"}},
        {"type": "tool_use", "name": "Write", "parameters": {"file_path": "/test.txt"}},
    ]

    lines = [orjson.dumps(line).decode() for line in test_data]
    test_file.write_text("\n".join(lines) + "\n")

    return str(test_file)


@pytest.fixture
def capture_exit():
    """Capture sys.exit calls for testing.

    Returns an ExitCapture object that records exit codes.
    """

    class ExitCapture:
        def __init__(self):
            self.code: Optional[int] = None
            self.called: bool = False

        def __call__(self, code: int = 0):
            self.code = code
            self.called = True
            raise SystemExit(code)

    return ExitCapture()


@pytest.fixture
def echo_test_script(tmp_path):
    """Create a test hook script for echo pipe testing.

    Returns path to a executable Python script that uses hook functions.
    """
    script = tmp_path / "test_hook.py"
    script.write_text(
        """#!/usr/bin/env python3
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if data.tool_name == "Write":
    if "/etc/passwd" in str(data.tool_input.get("file_path", "")):
        exit_block("Protected file")
exit_success()
"""
    )
    script.chmod(0o755)
    return str(script)


# Performance testing fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance tests."""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed = None

        def __enter__(self):
            self.start_time = time.perf_counter()
            return self

        def __exit__(self, *args):
            self.elapsed = time.perf_counter() - self.start_time

    return Timer()
