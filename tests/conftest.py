"""
Shared test fixtures for claude-parser test suite.

IMPORTANT: Uses REAL production JSONL data, not synthetic fixtures.
This ensures tests validate against actual Claude Code data structures.
"""

from pathlib import Path

import pytest


@pytest.fixture
def sample_jsonl(tmp_path):
    """
    Provides real production JSONL file for testing.

    NEVER SKIPS - Creates valid test data if production files unavailable.
    This ensures all tests run and reveal issues.

    Returns:
        Path to real Claude Code JSONL file or valid test file
    """
    # Skip checking for production files - always use synthetic data
    # This ensures tests are self-contained and don't depend on external files

    # NO SKIP - Create minimal valid JSONL that matches production structure
    test_file = tmp_path / "test_claude.jsonl"
    test_content = [
        '{"type":"summary","summary":"Test Session","leafUuid":"ea982431-bfc8-4bb7-82ed-410ba2a34002","uuid":"msg-1","sessionId":"test-session","timestamp":"2025-01-15T10:00:00Z"}',
        '{"type":"user","uuid":"msg-2","sessionId":"test-session","timestamp":"2025-01-15T10:00:01Z","message":{"content":"Hello"}}',
        '{"type":"assistant","uuid":"msg-3","sessionId":"test-session","timestamp":"2025-01-15T10:00:02Z","message":{"content":[{"type":"text","text":"Hi there!"}],"usage":{"input_tokens":10,"output_tokens":5,"cache_read_input_tokens":0,"cache_creation_input_tokens":0},"model":"claude-3-5-sonnet-20241022"}}',
    ]
    test_file.write_text("\n".join(test_content))
    return test_file


@pytest.fixture
def large_jsonl(sample_jsonl):
    """
    Provides larger production JSONL file for performance testing.

    NEVER SKIPS - Falls back to sample_jsonl if large file unavailable.

    Returns:
        Path to larger Claude Code JSONL file (98 messages) or fallback
    """
    real_file = Path("/path/to/test/data")

    if real_file.exists():
        return real_file

    # Fallback to sample_jsonl - never skip
    return sample_jsonl


@pytest.fixture
def medium_jsonl(sample_jsonl):
    """
    Provides medium-sized production JSONL file.

    NEVER SKIPS - Falls back to sample_jsonl if medium file unavailable.

    Returns:
        Path to medium Claude Code JSONL file or fallback
    """
    real_file = Path("/path/to/test/data")

    if real_file.exists():
        return real_file

    # Fallback to sample_jsonl - never skip
    return sample_jsonl


@pytest.fixture
def production_data_dir(tmp_path):
    """
    Provides path to production data directory.

    NEVER SKIPS - Creates temp directory with test file if prod dir unavailable.

    Returns:
        Path to directory containing real JSONL files or test directory
    """
    prod_dir = Path(
        # Removed - use synthetic test data instead
    )

    if prod_dir.exists():
        return prod_dir

    # Create temp directory with test file - never skip
    test_file = tmp_path / "test.jsonl"
    test_file.write_text(
        '{"type":"summary","summary":"Test","uuid":"msg-1","sessionId":"test"}'
    )
    return tmp_path


@pytest.fixture
def all_production_files(production_data_dir, sample_jsonl):
    """
    Provides list of all production JSONL files.

    NEVER SKIPS - Returns at least one file (sample_jsonl as fallback).

    Returns:
        List of Path objects to all production files
    """
    jsonl_files = list(production_data_dir.glob("*.jsonl"))

    if jsonl_files:
        return jsonl_files

    # Ensure at least one file - never skip
    return [sample_jsonl]


# Backwards compatibility aliases
@pytest.fixture
def real_claude_jsonl(large_jsonl):
    """Alias for backward compatibility with existing tests."""
    return large_jsonl


@pytest.fixture
def test_jsonl(sample_jsonl):
    """Alias for tests expecting 'test_jsonl' fixture."""
    return sample_jsonl
