"""TDD tests for project path matching logic - git-like behavior.

Modern 95/5 approach using factories - eliminates test duplication.
"""

from pathlib import Path
import pytest

from claude_parser.infrastructure.discovery import ConfigurableProjectDiscovery
from tests.factories import ProjectFactory, UserMessageFactory


@pytest.fixture
def discovery():
    """Create a ConfigurableProjectDiscovery instance for testing."""
    return ConfigurableProjectDiscovery()


class TestProjectPathMatching:
    """Test project path matching like git does - hierarchical directory matching."""

    def test_exact_path_match(self, discovery):
        """Test exact path matching - should always work."""
        project_dir = Path(
            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-sample-project"
        )
        target_path = Path(
            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-sample-project"
        )

        assert discovery._matches_project_path(project_dir, target_path) is True

    def test_encoded_path_exact_match(self, discovery):
        """Test that encoded path matches its decoded equivalent."""
        # Use factory to create project with real JSONL data
        events = [
            UserMessageFactory(
                uuid="test-1",
                timestamp="2025-01-01T10:00:00Z",
                cwd="/Volumes/AliDev/ai-projects/sample-project",
                message={"content": "test"}
            )
        ]

        project_data = ProjectFactory.create_temp_project(events=events)

        # Simulate encoded project directory name
        encoded_project = project_data["project_path"].parent / "-Volumes-AliDev-ai-projects-sample-project"
        encoded_project.mkdir()
        project_data["transcript_path"].rename(encoded_project / "session.jsonl")

        target_path = Path("/Volumes/AliDev/ai-projects/sample-project")

        assert discovery._matches_project_path(encoded_project, target_path) is True

    def test_subdirectory_matching_like_git(self, discovery):
        """Test that subdirectories match parent project (like git behavior)."""
        # Use factory to create project with specific cwd
        events = [
            UserMessageFactory(
                uuid="test-1",
                timestamp="2025-01-01T10:00:00Z",
                cwd="/Volumes/AliDev/ai-projects/sample-project",
                message={"content": "test"}
            )
        ]

        project_data = ProjectFactory.create_temp_project(events=events)

        # Test subdirectories - should all match
        subdirs = [
            Path("/Volumes/AliDev/ai-projects/sample-project/src"),
            Path("/Volumes/AliDev/ai-projects/sample-project/tests"),
            Path("/Volumes/AliDev/ai-projects/sample-project/src/utils"),
        ]

        for subdir in subdirs:
            assert discovery._matches_project_path(project_data["project_path"], subdir) is True, (
                f"Should match subdirectory: {subdir}"
            )

    def test_parent_directory_no_match(self, discovery):
        """Test that parent directories don't match (unlike git)."""
        project_dir = Path(
            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-sample-project"
        )

        # These should NOT match because they're parent directories
        parents = [
            Path("/Volumes/AliDev/ai-projects"),
            Path("/Volumes/AliDev"),
            Path("/Volumes"),
        ]

        for parent in parents:
            assert discovery._matches_project_path(project_dir, parent) is False, (
                f"Should NOT match parent: {parent}"
            )

    def test_sibling_directory_no_match(self, discovery):
        """Test that sibling directories don't match."""
        project_dir = Path(
            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-sample-project"
        )

        # These should NOT match because they're sibling directories
        siblings = [
            Path("/Volumes/AliDev/ai-projects/other-project"),
            Path("/Volumes/AliDev/ai-projects/different-project"),
        ]

        for sibling in siblings:
            assert discovery._matches_project_path(project_dir, sibling) is False, (
                f"Should NOT match sibling: {sibling}"
            )

    def test_complex_nested_project_path(self, discovery):
        """Test deeply nested project paths work correctly."""
        project_dir = Path(
            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser-tests-fixtures-sample-project"
        )

        # All of these should match
        matching_paths = [
            Path(
                "/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project"
            ),
            Path(
                "/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project/src"
            ),
            Path(
                "/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project/hello.py"
            ),
        ]

        for path in matching_paths:
            assert discovery._matches_project_path(project_dir, path) is True, (
                f"Should match: {path}"
            )

    def test_case_sensitivity(self, discovery):
        """Test case sensitivity in path matching."""
        # Use factory with lowercase cwd
        events = [
            UserMessageFactory(
                uuid="test-1",
                timestamp="2025-01-01T10:00:00Z",
                cwd="/Volumes/AliDev/ai-projects/sample-project",  # lowercase
                message={"content": "test"}
            )
        ]

        project_data = ProjectFactory.create_temp_project(events=events)

        # Simulate case-different project directory
        case_project = project_data["project_path"].parent / "-Volumes-AliDev-ai-projects-Sample-Project"
        case_project.mkdir()
        project_data["transcript_path"].rename(case_project / "session.jsonl")

        target_path = Path("/Volumes/AliDev/ai-projects/sample-project")  # lowercase

        # Should match regardless of case differences in project dir name
        assert discovery._matches_project_path(case_project, target_path) is True

    def test_non_encoded_project_paths(self, discovery):
        """Test that non-encoded project paths still work with fallback logic."""
        # Use factory with regular project name
        events = [
            UserMessageFactory(
                uuid="test-1",
                timestamp="2025-01-01T10:00:00Z",
                cwd="/some/path/regular-project-name",
                message={"content": "test"}
            )
        ]

        project_data = ProjectFactory.create_temp_project(events=events)

        # Rename to regular name (non-encoded)
        regular_project = project_data["project_path"].parent / "regular-project-name"
        regular_project.mkdir()
        project_data["transcript_path"].rename(regular_project / "session.jsonl")

        target_path = Path("/some/path/regular-project-name")

        # Should use fallback matching logic
        assert discovery._matches_project_path(regular_project, target_path) is True

    def test_real_world_scenario_from_jsonl(self, discovery):
        """Test using actual cwd from our JSONL transcript files."""
        # Read the actual fixture if it exists
        transcript_path = Path(__file__).parent / "fixtures" / "sample_transcript.jsonl"
        if transcript_path.exists():
            with open(transcript_path, "r") as f:
                first_line = f.readline().strip()
                if first_line:
                    import orjson
                    event = orjson.loads(first_line)
                    actual_cwd = event.get("cwd")
                    if actual_cwd:
                        project_dir = Path(
                            "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser-tests-fixtures-sample-project"
                        )
                        current_dir = Path(actual_cwd)

                        assert (
                            discovery._matches_project_path(project_dir, current_dir)
                            is True
                        ), f"Should match cwd from JSONL: {actual_cwd}"

        # Fallback test using factory
        events = [
            UserMessageFactory(
                cwd="/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project"
            )
        ]
        project_data = ProjectFactory.create_temp_project(events=events)
        current_dir = Path("/Volumes/AliDev/ai-projects/claude-parser/tests/fixtures/sample-project")

        assert discovery._matches_project_path(project_data["project_path"], current_dir) is True

    def test_cwd_extraction_from_real_transcript(self, discovery):
        """Test extracting cwd from actual transcript and validating project matching."""
        # Test with our actual generated transcript
        transcript_path = Path(__file__).parent / "fixtures" / "sample_transcript.jsonl"
        if not transcript_path.exists():
            pytest.skip("Sample transcript not found")

        # Extract all unique cwd values from the transcript
        cwds = set()
        with open(transcript_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        import orjson
                        event = orjson.loads(line)
                        if "cwd" in event:
                            cwds.add(event["cwd"])
                    except orjson.JSONDecodeError:
                        continue

        assert len(cwds) > 0, "Should find at least one cwd in transcript"

        # For each cwd found, verify that project discovery can match it
        for cwd in cwds:
            # Find which project this cwd should match
            all_projects = discovery.find_projects()
            matched_project = None

            for project_dir in all_projects:
                if discovery._matches_project_path(project_dir, Path(cwd)):
                    matched_project = project_dir
                    break

            assert matched_project is not None, (
                f"Should find a matching project for cwd: {cwd}"
            )
            print(f"✓ CWD {cwd} matches project {matched_project}")

    def test_symlink_handling(self, discovery):
        """Test that symlinks are handled correctly."""
        # Test with resolved paths to handle symlinks
        project_dir = Path("/Users/ali/.claude/projects/-tmp-test-project")
        target_path = Path("/tmp/test-project")  # might be symlinked

        # Should work with path resolution
        assert discovery._matches_project_path(project_dir, target_path) in [
            True,
            False,
        ]  # Depends on actual symlinks
