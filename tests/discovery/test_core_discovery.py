"""
Discovery Domain: Core Features

Tests 95% use case discovery functions - interface only.
"""

from pathlib import Path
from claude_parser.discovery import find_current_transcript, find_transcript_for_cwd
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

    def test_discovery_handles_nonexistent_paths_gracefully(self):
        """Interface: Discovery handles non-existent paths gracefully."""
        nonexistent_path = Path("/definitely/does/not/exist")

        # Should not crash, return None
        transcript = find_transcript_for_cwd(nonexistent_path)
        assert transcript is None
