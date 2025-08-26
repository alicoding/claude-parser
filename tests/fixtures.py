"""
Test fixtures using real Claude Code JSONL production data.

SOLID: Single responsibility - only test fixtures
95/5: Using real production data from actual Claude sessions
NO MOCKS: All tests use real JSONL files from jsonl-prod-data-for-test/
"""

from pathlib import Path

import pytest


def get_real_claude_jsonl_files():
    """Get real Claude JSONL files for testing from production data."""
    # Use the production test data directory
    prod_data_dir = Path(__file__).parent.parent / "jsonl-prod-data-for-test"

    # Get all JSONL files from production data
    jsonl_files = []
    for jsonl_file in prod_data_dir.rglob("*.jsonl"):
        if jsonl_file.is_file():
            jsonl_files.append(jsonl_file)

    # Sort by size for predictable testing
    jsonl_files.sort(key=lambda f: f.stat().st_size)

    return jsonl_files


@pytest.fixture
def small_claude_jsonl():
    """Fixture providing a small Claude JSONL file (edge case: 1 line)."""
    files = get_real_claude_jsonl_files()
    if not files:
        pytest.skip("No real Claude JSONL files found")
    return files[0]  # Smallest file (summary-only)


@pytest.fixture
def medium_claude_jsonl():
    """Fixture providing a medium-sized Claude JSONL file (~100 lines)."""
    files = get_real_claude_jsonl_files()
    if len(files) < 2:
        pytest.skip("Not enough Claude JSONL files for medium test")
    return files[1]  # Medium file


@pytest.fixture
def large_claude_jsonl():
    """Fixture providing a large Claude JSONL file (1000+ lines)."""
    files = get_real_claude_jsonl_files()
    if len(files) < 3:
        pytest.skip("Not enough Claude JSONL files for large test")
    return files[2]  # Largest file


@pytest.fixture
def real_claude_jsonl():
    """Default fixture for any real Claude JSONL file."""
    files = get_real_claude_jsonl_files()
    if len(files) < 2:
        pytest.skip("Not enough Claude JSONL files")
    return files[1]  # Medium file


@pytest.fixture
def all_real_claude_jsonls():
    """Fixture providing all available real Claude JSONL files."""
    files = get_real_claude_jsonl_files()
    if not files:
        pytest.skip("No real Claude JSONL files found")
    return files


@pytest.fixture
def sample_jsonl():
    """Legacy fixture name for backwards compatibility."""
    files = get_real_claude_jsonl_files()
    if len(files) < 2:
        pytest.skip("Not enough Claude JSONL files")
    return files[1]  # Medium file
