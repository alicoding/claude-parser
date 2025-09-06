"""
Discovery service - Clean ResourceManager architecture.

95/5 + Centralized Resources + Micro-Components pattern.
All components 5-20 LOC, framework does heavy lifting.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from ..core.resources import get_resource_manager
from ..components.project_finder import ProjectFinder
from ..components.transcript_finder import TranscriptFinder


class DiscoveryService:
    """Clean discovery service using ResourceManager pattern."""

    def __init__(self):
        """Initialize with centralized resources."""
        self.resources = get_resource_manager()
        self.project_finder = ProjectFinder(self.resources)
        self.transcript_finder = TranscriptFinder(self.resources)

    def find_current_transcript(self, cwd: Optional[Path] = None) -> Optional[str]:
        """Find transcript for current/specified directory."""
        if cwd is None:
            cwd = Path.cwd()

        project_dir = self.project_finder.find_current_project(cwd)
        if not project_dir:
            return None

        transcript_path = self.transcript_finder.get_most_recent(project_dir)
        return str(transcript_path) if transcript_path else None

    def find_all_transcripts(self, cwd: Optional[Path] = None) -> List[str]:
        """Find all transcript files for current/specified directory."""
        if cwd is None:
            cwd = Path.cwd()

        project_dir = self.project_finder.find_current_project(cwd)
        if not project_dir:
            return []

        transcript_paths = self.transcript_finder.get_transcripts(project_dir)
        return [str(p) for p in transcript_paths]


# 95/5 Factory Functions (Public API)
def find_current_transcript() -> Optional[str]:
    """Find transcript for current working directory - 95% use case."""
    service = DiscoveryService()
    return service.find_current_transcript()


def find_transcript_for_cwd(project_path: Path) -> Optional[str]:
    """Find transcript for specific project directory - 5% use case."""
    service = DiscoveryService()
    return service.find_current_transcript(project_path)


def find_all_transcripts_for_cwd(project_path: Path) -> List[str]:
    """Find all transcripts for project directory - 5% use case."""
    service = DiscoveryService()
    return service.find_all_transcripts(project_path)


# Additional compatibility functions
def list_all_projects() -> List[Dict[str, Any]]:
    """List all Claude projects - maintain compatibility."""
    # Use existing implementation temporarily
    from .transcript_finder import list_all_projects as legacy_list_all_projects
    return legacy_list_all_projects()


def find_project_by_original_path(target_path: str | Path) -> Optional[Dict[str, Any]]:
    """Find project by original path - maintain compatibility."""
    from .transcript_finder import find_project_by_original_path as legacy_find_project_by_original_path
    return legacy_find_project_by_original_path(target_path)


def find_project_by_encoded_name(encoded_name: str) -> Optional[Dict[str, Any]]:
    """Find project by encoded name - maintain compatibility."""
    from .transcript_finder import find_project_by_encoded_name as legacy_find_project_by_encoded_name
    return legacy_find_project_by_encoded_name(encoded_name)
