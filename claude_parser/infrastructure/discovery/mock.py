"""Mock project discovery implementation for testing."""

from pathlib import Path
from typing import Dict, List, Optional

from claude_parser.domain.interfaces import ProjectDiscoveryInterface


class MockProjectDiscovery(ProjectDiscoveryInterface):
    """Mock project discovery implementation for isolated testing.

    This implementation allows tests to provide mock project data
    without requiring filesystem access or real Claude Code projects.
    """

    def __init__(self, mock_projects: Optional[Dict[str, Path]] = None):
        """Initialize with mock project data.

        Args:
            mock_projects: Dictionary mapping project names to paths.
                          If None, initializes with empty project set.
        """
        self.mock_projects = mock_projects or {}
        self.mock_transcripts: Dict[Path, List[Path]] = {}

    def add_project(self, name: str, path: Path, transcripts: Optional[List[Path]] = None):
        """Add a mock project for testing.

        Args:
            name: Project name identifier.
            path: Project path.
            transcripts: Optional list of transcript file paths for this project.
        """
        self.mock_projects[name] = path
        if transcripts:
            self.mock_transcripts[path] = transcripts

    def find_projects(self) -> List[Path]:
        """Return all mock project paths.

        Returns:
            List of mock project paths.
        """
        return list(self.mock_projects.values())

    def find_current_project(self, cwd: Path) -> Optional[Path]:
        """Find mock project matching the current working directory.

        Args:
            cwd: Current working directory to match.

        Returns:
            Mock project path if found, None otherwise.
        """
        cwd_resolved = cwd.resolve()

        # Find project by exact path match
        for project_path in self.mock_projects.values():
            if project_path.resolve() == cwd_resolved:
                return project_path

            # Check if cwd is a subdirectory of project
            try:
                cwd_resolved.relative_to(project_path.resolve())
                return project_path
            except ValueError:
                continue

        return None

    def get_project_transcripts(self, project_path: Path) -> List[Path]:
        """Get mock transcript files for a project.

        Args:
            project_path: Path to the project directory.

        Returns:
            List of mock transcript file paths.
        """
        return self.mock_transcripts.get(project_path, [])

    def is_project_directory(self, path: Path) -> bool:
        """Check if path is a mock project directory.

        Args:
            path: Directory path to check.

        Returns:
            True if path is in mock_projects.
        """
        return path in self.mock_projects.values()

    def clear_projects(self):
        """Clear all mock project data."""
        self.mock_projects.clear()
        self.mock_transcripts.clear()
