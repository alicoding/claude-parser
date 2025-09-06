"""Project discovery interface for dependency injection and testing."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class ProjectDiscoveryInterface(ABC):
    """Abstract interface for discovering Claude Code projects.

    This interface allows for different discovery implementations:
    - ConfigurableProjectDiscovery: Uses configurable filesystem paths
    - MockProjectDiscovery: For testing with mock data
    - RemoteProjectDiscovery: For future cloud-based project discovery
    """

    @abstractmethod
    def find_projects(self) -> List[Path]:
        """Find all available Claude Code projects.

        Returns:
            List of project paths that contain Claude Code sessions.
        """
        pass

    @abstractmethod
    def find_current_project(self, cwd: Path) -> Optional[Path]:
        """Find the Claude Code project for the current working directory.

        Args:
            cwd: Current working directory to search from.

        Returns:
            Project path if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_project_transcripts(self, project_path: Path) -> List[Path]:
        """Get all transcript files for a specific project.

        Args:
            project_path: Path to the project directory.

        Returns:
            List of JSONL transcript file paths.
        """
        pass

    @abstractmethod
    def is_project_directory(self, path: Path) -> bool:
        """Check if a directory contains Claude Code project data.

        Args:
            path: Directory path to check.

        Returns:
            True if the directory contains Claude Code transcripts.
        """
        pass
