"""Tests for cross-platform project discovery system."""

import os
import tempfile
from pathlib import Path

import pytest

from claude_parser.domain.interfaces import ProjectDiscoveryInterface
from claude_parser.infrastructure.discovery import ConfigurableProjectDiscovery, MockProjectDiscovery
from claude_parser.infrastructure.platform import get_claude_projects_dir, get_platform_config_dir


class TestPlatformPaths:
    """Test cross-platform path resolution."""

    def test_get_platform_config_dir_unix(self, monkeypatch):
        """Test XDG directory resolution on Unix systems."""
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.setenv("XDG_CONFIG_HOME", "/custom/config")

        config_dir = get_platform_config_dir()
        assert config_dir == Path("/custom/config")

    def test_get_platform_config_dir_unix_default(self, monkeypatch):
        """Test default XDG directory on Unix."""
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        config_dir = get_platform_config_dir()
        assert config_dir == Path.home() / ".config"

    def test_get_platform_config_dir_windows(self, monkeypatch):
        """Test AppData directory resolution on Windows."""
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")

        config_dir = get_platform_config_dir()
        assert config_dir == Path("C:\\Users\\Test\\AppData\\Roaming")

    def test_get_claude_projects_dir_override(self, monkeypatch):
        """Test CLAUDE_PROJECTS_DIR environment variable override."""
        custom_path = "/workspace/claude-projects"
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", custom_path)

        projects_dir = get_claude_projects_dir()
        assert projects_dir == Path(custom_path)

    def test_get_claude_projects_dir_default_unix(self, monkeypatch):
        """Test default projects directory on Unix."""
        monkeypatch.setattr("sys.platform", "linux")
        monkeypatch.delenv("CLAUDE_PROJECTS_DIR", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        projects_dir = get_claude_projects_dir()
        assert projects_dir == Path.home() / ".config" / "claude" / "projects"

    def test_get_claude_projects_dir_default_windows(self, monkeypatch):
        """Test default projects directory on Windows."""
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.delenv("CLAUDE_PROJECTS_DIR", raising=False)
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")

        projects_dir = get_claude_projects_dir()
        assert projects_dir == Path("C:\\Users\\Test\\AppData\\Roaming") / "Claude" / "projects"


class TestMockProjectDiscovery:
    """Test MockProjectDiscovery implementation."""

    def test_empty_mock_discovery(self, mock_discovery):
        """Test MockProjectDiscovery with no projects."""
        assert mock_discovery.find_projects() == []
        assert mock_discovery.find_current_project(Path.cwd()) is None
        assert mock_discovery.get_project_transcripts(Path("/nonexistent")) == []
        assert not mock_discovery.is_project_directory(Path("/nonexistent"))

    def test_mock_discovery_with_projects(self, mock_discovery_with_projects):
        """Test MockProjectDiscovery with sample projects."""
        projects = mock_discovery_with_projects.find_projects()
        assert len(projects) == 2

        # Test project directory detection
        for project in projects:
            assert mock_discovery_with_projects.is_project_directory(project)
            transcripts = mock_discovery_with_projects.get_project_transcripts(project)
            assert len(transcripts) > 0

    def test_mock_discovery_add_project(self, mock_discovery):
        """Test adding projects to MockProjectDiscovery."""
        project_path = Path("/test/project")
        transcript_path = Path("/test/project/session.jsonl")

        mock_discovery.add_project("test", project_path, [transcript_path])

        assert project_path in mock_discovery.find_projects()
        assert mock_discovery.is_project_directory(project_path)
        assert mock_discovery.get_project_transcripts(project_path) == [transcript_path]

    def test_mock_discovery_find_current_project(self, mock_discovery):
        """Test finding current project in MockProjectDiscovery."""
        project_path = Path("/workspace/myproject")
        mock_discovery.add_project("test", project_path)

        # Exact match
        found = mock_discovery.find_current_project(project_path)
        assert found == project_path

        # Subdirectory match
        subdir = project_path / "src"
        found = mock_discovery.find_current_project(subdir)
        assert found == project_path


class TestConfigurableProjectDiscovery:
    """Test ConfigurableProjectDiscovery implementation."""

    def test_configurable_discovery_no_projects_dir(self, isolated_claude_env):
        """Test ConfigurableProjectDiscovery with non-existent projects directory."""
        # isolated_claude_env sets CLAUDE_PROJECTS_DIR but directory is empty
        discovery = ConfigurableProjectDiscovery()

        assert discovery.find_projects() == []
        assert discovery.find_current_project(Path.cwd()) is None

    def test_configurable_discovery_with_projects(self, sample_claude_project):
        """Test ConfigurableProjectDiscovery with actual project structure."""
        project_path, transcript_paths = sample_claude_project

        # Create discovery pointing to the parent directory containing the project
        discovery = ConfigurableProjectDiscovery(project_path.parent)

        projects = discovery.find_projects()
        assert len(projects) >= 1
        assert project_path in projects

        # Test transcript discovery
        transcripts = discovery.get_project_transcripts(project_path)
        assert len(transcripts) == len(transcript_paths)

    def test_configurable_discovery_project_detection(self, sample_claude_project):
        """Test project directory detection."""
        project_path, _ = sample_claude_project

        discovery = ConfigurableProjectDiscovery()

        # Should detect project directory with JSONL files
        assert discovery.is_project_directory(project_path)

        # Should not detect empty directory
        empty_dir = project_path.parent / "empty"
        empty_dir.mkdir()
        assert not discovery.is_project_directory(empty_dir)

    def test_configurable_discovery_environment_override(self, monkeypatch):
        """Test that ConfigurableProjectDiscovery respects CLAUDE_PROJECTS_DIR."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            monkeypatch.setenv("CLAUDE_PROJECTS_DIR", str(temp_path))

            discovery = ConfigurableProjectDiscovery()

            # Should use the environment variable path (resolve symlinks for comparison)
            assert discovery.projects_dir == temp_path.resolve()


class TestProjectDiscoveryIntegration:
    """Integration tests for project discovery system."""

    def test_discovery_interface_compliance(self):
        """Test that implementations comply with ProjectDiscoveryInterface."""
        # Test MockProjectDiscovery
        mock = MockProjectDiscovery()
        assert isinstance(mock, ProjectDiscoveryInterface)

        # Test ConfigurableProjectDiscovery
        configurable = ConfigurableProjectDiscovery()
        assert isinstance(configurable, ProjectDiscoveryInterface)

    def test_docker_environment_simulation(self, monkeypatch):
        """Test behavior in Docker-like environment."""
        # Simulate Docker container environment
        monkeypatch.setenv("HOME", "/root")
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setattr("sys.platform", "linux")

        # Set custom projects directory (like volume mount)
        projects_dir = "/workspace/claude-projects"
        monkeypatch.setenv("CLAUDE_PROJECTS_DIR", projects_dir)

        # Should resolve to custom directory
        resolved = get_claude_projects_dir()
        assert resolved == Path(projects_dir)

        # ConfigurableProjectDiscovery should use it
        discovery = ConfigurableProjectDiscovery()
        assert discovery.projects_dir == Path(projects_dir)

    def test_ci_environment_simulation(self, monkeypatch, isolated_claude_env):
        """Test behavior in CI/CD environment (like GitHub Actions)."""
        # Simulate GitHub Actions environment
        monkeypatch.setenv("CI", "true")
        monkeypatch.setenv("GITHUB_ACTIONS", "true")
        monkeypatch.setenv("HOME", "/home/runner")

        # Use isolated environment for testing
        discovery = ConfigurableProjectDiscovery()

        # Should not crash even with no projects
        projects = discovery.find_projects()
        assert isinstance(projects, list)  # Should return empty list, not crash

    def test_windows_environment_simulation(self, monkeypatch):
        """Test behavior on Windows environment."""
        # Simulate Windows environment
        monkeypatch.setattr("sys.platform", "win32")
        monkeypatch.setenv("APPDATA", "C:\\Users\\TestUser\\AppData\\Roaming")
        monkeypatch.delenv("CLAUDE_PROJECTS_DIR", raising=False)

        projects_dir = get_claude_projects_dir()
        expected = Path("C:\\Users\\TestUser\\AppData\\Roaming") / "Claude" / "projects"
        assert projects_dir == expected
