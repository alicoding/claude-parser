"""
Discovery Domain: Transcript Discovery Features

Tests ALL discovery functions from claude_parser.discovery public API:
- find_current_transcript() - 95% use case
- find_transcript_for_cwd() - 5% use case
- find_all_transcripts_for_cwd() - All transcripts
- list_all_projects() - Project listing
- find_project_by_original_path() - Find by path
- find_project_by_encoded_name() - Find by name

INTERFACE ONLY - No infrastructure, no fake data, no custom code.
"""

from pathlib import Path
from claude_parser.discovery import (
    find_current_transcript,
    find_transcript_for_cwd,
    find_all_transcripts_for_cwd,
    list_all_projects,
    find_project_by_original_path,
    find_project_by_encoded_name,
)
from ..framework import EnforcedTestBase


class TestCoreDiscoveryFeatures(EnforcedTestBase):
    """Test core discovery features - 95% use case."""

    def test_find_current_transcript_returns_path_or_none(self):
        """Interface: find_current_transcript() returns str path or None."""
        transcript = find_current_transcript()

        # Interface contract
        assert transcript is None or isinstance(transcript, str)

        # If found, should be a .jsonl file
        if transcript:
            assert transcript.endswith('.jsonl')

    def test_find_transcript_for_cwd_accepts_path(self):
        """Interface: find_transcript_for_cwd() accepts Path, returns str or None."""
        current_dir = Path.cwd()
        transcript = find_transcript_for_cwd(current_dir)

        # Interface contract
        assert transcript is None or isinstance(transcript, str)

        # If found, should be a .jsonl file
        if transcript:
            assert transcript.endswith('.jsonl')


class TestAdvancedDiscoveryFeatures(EnforcedTestBase):
    """Test advanced discovery features - 5% use case."""

    def test_find_all_transcripts_for_cwd_returns_list(self):
        """Interface: find_all_transcripts_for_cwd() returns list of strings."""
        current_dir = Path.cwd()
        transcripts = find_all_transcripts_for_cwd(current_dir)

        # Interface contract - always returns list
        assert isinstance(transcripts, list)

        # All items should be strings
        for transcript in transcripts:
            assert isinstance(transcript, str)
            assert transcript.endswith('.jsonl')

    def test_list_all_projects_returns_list_of_dicts(self):
        """Interface: list_all_projects() returns list of project dicts."""
        projects = list_all_projects()

        # Interface contract - always returns list
        assert isinstance(projects, list)

        # Each project should be a dict with project info
        for project in projects:
            assert isinstance(project, dict)

    def test_find_project_by_original_path_accepts_string_or_path(self):
        """Interface: find_project_by_original_path() accepts str/Path, returns dict or None."""
        # Test with string path
        project_str = find_project_by_original_path("/some/path")
        assert project_str is None or isinstance(project_str, dict)

        # Test with Path object
        project_path = find_project_by_original_path(Path("/some/path"))
        assert project_path is None or isinstance(project_path, dict)

    def test_find_project_by_encoded_name_accepts_string(self):
        """Interface: find_project_by_encoded_name() accepts string, returns dict or None."""
        project = find_project_by_encoded_name("some-encoded-name")

        # Interface contract
        assert project is None or isinstance(project, dict)


class TestDiscoveryEdgeCases(EnforcedTestBase):
    """Test discovery edge cases and error handling."""

    def test_discovery_handles_nonexistent_paths_gracefully(self):
        """Interface: Discovery functions handle non-existent paths gracefully."""
        nonexistent_path = Path("/definitely/does/not/exist")

        # Should not crash, return None or empty list
        transcript = find_transcript_for_cwd(nonexistent_path)
        assert transcript is None

        transcripts = find_all_transcripts_for_cwd(nonexistent_path)
        assert isinstance(transcripts, list)
        assert len(transcripts) == 0

    def test_discovery_handles_empty_strings_gracefully(self):
        """Interface: Discovery functions handle edge case inputs gracefully."""
        # Empty string should not crash
        project = find_project_by_original_path("")
        assert project is None or isinstance(project, dict)

        encoded_project = find_project_by_encoded_name("")
        assert encoded_project is None or isinstance(encoded_project, dict)
