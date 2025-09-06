"""
Minimal test configuration - Focus on FEATURES not infrastructure.

Simple fixtures for testing public API features:
- load() - Can I load a conversation?
- watch() - Can I watch for changes?
- find_current_transcript() - Can I discover transcripts?
"""

from pathlib import Path
import pytest


@pytest.fixture
def sample_transcript() -> Path:
    """Real Claude Code transcript using discovery API."""
    from claude_parser import find_current_transcript

    transcript = find_current_transcript()
    if transcript and transcript.exists():
        return transcript

    pytest.skip("No transcript found. Run `claude -p` to create project context.")


@pytest.fixture
def empty_jsonl_file(tmp_path) -> Path:
    """Empty JSONL file for edge case testing."""
    tmp_file = tmp_path / "empty.jsonl"
    tmp_file.touch()
    return tmp_file


# Clean, minimal fixtures using REAL Claude Code data
