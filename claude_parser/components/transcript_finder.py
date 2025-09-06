"""
TranscriptFinder micro-component - Find transcript files.

95/5 principle: Simple file operations, framework handles sorting.
Size: ~15 LOC (LLM-readable in single context)
"""

from pathlib import Path
from typing import List, Optional
from ..core.resources import ResourceManager


class TranscriptFinder:
    """Micro-component: Find and sort transcript files."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def get_transcripts(self, project_dir: Path, most_recent_only: bool = False) -> List[Path]:
        """Get transcript files from project directory."""
        if not project_dir.exists() or not project_dir.is_dir():
            return []

        # Get all JSONL files
        transcripts = [f for f in project_dir.iterdir() if f.is_file() and f.suffix == '.jsonl']

        # Sort by modification time (newest first)
        transcripts.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        return transcripts[:1] if most_recent_only else transcripts

    def get_most_recent(self, project_dir: Path) -> Optional[Path]:
        """Get most recent transcript file."""
        transcripts = self.get_transcripts(project_dir, most_recent_only=True)
        return transcripts[0] if transcripts else None
