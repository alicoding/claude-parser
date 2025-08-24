"""
Test fixtures using real Claude Code JSONL files.

SOLID: Single responsibility - only test fixtures
95/5: Using real data from actual Claude sessions
"""

from pathlib import Path
import pytest


def get_real_claude_jsonl_files():
    """Get real Claude JSONL files for testing."""
    claude_projects = Path.home() / ".claude" / "projects"
    
    # Known good JSONL files with substantial data
    known_files = [
        # Hook system v2 project - has lots of real messages
        claude_projects / "-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2" / "8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl",
        claude_projects / "-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2" / "8bca8a40-dfa2-417c-bc16-f486af4d906f.jsonl",
        # Current claude-parser project
        claude_projects / "claude-parser" / "test_manual.jsonl",
    ]
    
    # Return files that actually exist
    return [f for f in known_files if f.exists()]


@pytest.fixture
def real_claude_jsonl():
    """Fixture providing a real Claude JSONL file."""
    files = get_real_claude_jsonl_files()
    if not files:
        pytest.skip("No real Claude JSONL files found")
    return files[0]


@pytest.fixture
def medium_claude_jsonl():
    """Fixture providing a medium-sized Claude JSONL file (3-10MB)."""
    claude_projects = Path.home() / ".claude" / "projects"
    medium_file = claude_projects / "-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2" / "8bca8a40-dfa2-417c-bc16-f486af4d906f.jsonl"
    
    if not medium_file.exists():
        pytest.skip("Medium Claude JSONL file not found")
    return medium_file


@pytest.fixture
def large_claude_jsonl():
    """Fixture providing a large Claude JSONL file (30MB+)."""
    claude_projects = Path.home() / ".claude" / "projects"
    large_file = claude_projects / "-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2" / "2f283580-c24a-40af-8129-1be80c07b965.jsonl"
    
    if not large_file.exists():
        pytest.skip("Large Claude JSONL file not found")
    return large_file


@pytest.fixture
def all_real_claude_jsonls():
    """Fixture providing all available real Claude JSONL files."""
    files = get_real_claude_jsonl_files()
    if not files:
        pytest.skip("No real Claude JSONL files found")
    return files