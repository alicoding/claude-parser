"""Test fixtures for project discovery testing."""

import tempfile
from pathlib import Path
from typing import List

import pytest

from claude_parser.infrastructure.discovery import MockProjectDiscovery


@pytest.fixture
def mock_projects_dir():
    """Create a temporary directory for mock Claude projects."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_discovery():
    """Create a MockProjectDiscovery with no projects."""
    return MockProjectDiscovery()


@pytest.fixture
def mock_discovery_with_projects(mock_projects_dir):
    """Create a MockProjectDiscovery with sample projects."""
    discovery = MockProjectDiscovery()

    # Create mock project directories
    project1 = mock_projects_dir / "project1"
    project2 = mock_projects_dir / "project2"
    project1.mkdir()
    project2.mkdir()

    # Create mock transcript files
    transcript1 = project1 / "session1.jsonl"
    transcript2 = project1 / "session2.jsonl"
    transcript3 = project2 / "session1.jsonl"

    # Write minimal JSONL content
    sample_jsonl = '{"type": "user", "uuid": "test-uuid", "message": {"content": "test"}}\n'
    transcript1.write_text(sample_jsonl)
    transcript2.write_text(sample_jsonl)
    transcript3.write_text(sample_jsonl)

    # Add projects to mock discovery
    discovery.add_project("project1", project1, [transcript1, transcript2])
    discovery.add_project("project2", project2, [transcript3])

    return discovery


@pytest.fixture
def claude_projects_dir_env(monkeypatch, mock_projects_dir):
    """Set CLAUDE_PROJECTS_DIR environment variable for testing."""
    monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(mock_projects_dir))
    yield mock_projects_dir


@pytest.fixture
def isolated_claude_env(monkeypatch, mock_projects_dir):
    """Create an isolated Claude environment for testing.

    This fixture:
    - Sets CLAUDE_PROJECTS_DIR to a temporary directory
    - Ensures no interference with real Claude projects
    - Provides a clean test environment for each test
    """
    # Set environment variables
    monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(mock_projects_dir))

    # Clean any existing XDG variables that might interfere
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

    yield mock_projects_dir


@pytest.fixture
def sample_claude_project(isolated_claude_env):
    """Create a sample Claude Code project structure for testing.

    Returns:
        Tuple[Path, List[Path]]: (project_path, transcript_paths)
    """
    # Create project directory
    project_path = isolated_claude_env / "sample-project"
    project_path.mkdir(parents=True)

    # Create sample transcript files
    transcripts = []
    for i in range(2):
        transcript_path = project_path / f"session{i+1}.jsonl"

        # Write realistic Claude Code JSONL content
        sample_events = [
            {
                "type": "user",
                "uuid": f"user-{i}-1",
                "sessionId": f"session-{i}",
                "timestamp": "2025-01-01T00:00:00Z",
                "message": {"content": "Hello"}
            },
            {
                "type": "assistant",
                "uuid": f"asst-{i}-1",
                "sessionId": f"session-{i}",
                "timestamp": "2025-01-01T00:00:01Z",
                "message": {
                    "content": [
                        {"type": "text", "text": "Hi there!"},
                        {
                            "type": "tool_use",
                            "id": f"tool-{i}",
                            "name": "Write",
                            "input": {
                                "file_path": "/test/file.py",
                                "content": "print('Hello')"
                            }
                        }
                    ]
                }
            }
        ]

        with open(transcript_path, 'w') as f:
            for event in sample_events:
                f.write(f"{event}\n")

        transcripts.append(transcript_path)

    return project_path, transcripts
