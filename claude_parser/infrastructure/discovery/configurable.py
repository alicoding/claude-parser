"""Configurable project discovery implementation using filesystem scanning."""

import os
from pathlib import Path
from typing import List, Optional

from claude_parser.domain.interfaces import ProjectDiscoveryInterface
from claude_parser.infrastructure.platform import get_claude_projects_dir


class ConfigurableProjectDiscovery(ProjectDiscoveryInterface):
    """Filesystem-based project discovery with environment variable configuration.

    This implementation:
    - Respects CLAUDE_PROJECTS_DIR environment variable
    - Follows XDG/AppData conventions by default
    - Works across Windows, macOS, Linux, Docker, cloud IDEs
    - Gracefully handles missing or inaccessible directories
    """

    def __init__(self, projects_dir: Optional[Path] = None):
        """Initialize with optional custom projects directory.

        Args:
            projects_dir: Optional custom projects directory.
                         If None, uses get_claude_projects_dir() with env var support.
        """
        self.projects_dir = projects_dir or get_claude_projects_dir()

    def find_projects(self) -> List[Path]:
        """Find all available Claude Code projects by scanning the projects directory.

        Returns:
            List of project paths that contain JSONL transcript files.
        """
        if not self._is_projects_dir_accessible():
            return []

        projects = []
        try:
            # Scan projects directory for subdirectories with JSONL files
            for item in self.projects_dir.iterdir():
                if item.is_dir() and self.is_project_directory(item):
                    projects.append(item)
        except (OSError, PermissionError):
            # Handle cases where directory is not readable
            pass

        return sorted(projects)

    def find_current_project(self, cwd: Path) -> Optional[Path]:
        """Find the Claude Code project that matches the current working directory.

        Uses project name mapping from Claude Code's directory naming convention.

        Args:
            cwd: Current working directory to match against projects.

        Returns:
            Project path if found, None otherwise.
        """
        if not self._is_projects_dir_accessible():
            return None

        cwd_resolved = cwd.resolve()

        # Try to find project by exact path match first
        for project_dir in self.find_projects():
            if self._matches_project_path(project_dir, cwd_resolved):
                return project_dir

        return None

    def get_project_transcripts(self, project_path: Path) -> List[Path]:
        """Get all JSONL transcript files for a project.

        Args:
            project_path: Path to the project directory.

        Returns:
            List of JSONL transcript file paths sorted by modification time.
        """
        if not project_path.exists() or not project_path.is_dir():
            return []

        transcripts = []
        try:
            for file_path in project_path.iterdir():
                if file_path.is_file() and file_path.suffix == ".jsonl":
                    transcripts.append(file_path)
        except (OSError, PermissionError):
            pass

        # Sort by modification time (newest first)
        transcripts.sort(key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)
        return transcripts

    def is_project_directory(self, path: Path) -> bool:
        """Check if directory contains Claude Code JSONL transcript files.

        Args:
            path: Directory path to check.

        Returns:
            True if directory contains at least one .jsonl file.
        """
        if not path.exists() or not path.is_dir():
            return False

        try:
            for file_path in path.iterdir():
                if file_path.is_file() and file_path.suffix == ".jsonl":
                    return True
        except (OSError, PermissionError):
            pass

        return False

    def _is_projects_dir_accessible(self) -> bool:
        """Check if the projects directory exists and is accessible."""
        try:
            return self.projects_dir.exists() and self.projects_dir.is_dir() and os.access(self.projects_dir, os.R_OK)
        except (OSError, PermissionError):
            return False

    def _matches_project_path(self, project_dir: Path, target_path: Path) -> bool:
        """Check if a project directory matches the target path.

        This handles Claude Code's project naming conventions and path encoding.
        """
        # Direct path comparison
        if target_path == project_dir:
            return True

        # Check if target_path is contained within any project's original path
        # This requires parsing the project directory name which may be encoded
        try:
            # For now, use simple name matching - can be enhanced for path decoding
            project_name = project_dir.name
            target_name = target_path.name

            # Simple heuristic: check if project name contains target name or vice versa
            return (
                project_name.lower() in target_name.lower() or
                target_name.lower() in project_name.lower() or
                str(target_path) in project_name
            )
        except (OSError, AttributeError):
            return False
