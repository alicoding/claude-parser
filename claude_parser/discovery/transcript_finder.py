"""
Transcript discovery implementation.

Maps project paths to Claude Code transcript files.
Handles directory names and finds most recent sessions.
"""

from pathlib import Path
from typing import List, Optional

import orjson
from more_itertools import first as more_first
from toolz import filter as toolz_filter
from toolz import map as toolz_map


def find_current_transcript() -> Optional[str]:
    """Find transcript for current working directory.

    95% use case - auto-detect from where you are.

    Returns:
        Path to most recent transcript file, or None if not found

    Example:
        transcript = find_current_transcript()
        if transcript:
            conv = load(transcript)
    """
    return find_transcript_for_cwd(Path.cwd())


def find_transcript_for_cwd(project_path: Path) -> Optional[str]:
    """Find transcript for specific project directory.

    5% use case - explicit path for remote plugins, CI/CD, etc.

    Args:
        project_path: Path to project directory

    Returns:
        Path to most recent transcript file, or None if not found

    Example:
        # For remote plugin
        transcript = find_transcript_for_cwd(Path("/remote/project/path"))

        # For CI/CD
        from os import environ
        transcript = find_transcript_for_cwd(Path(environ["PROJECT_ROOT"]))
    """
    claude_projects = Path.home() / ".claude" / "projects"

    if not claude_projects.exists():
        return None

    # Normalize the project path
    project_path = project_path.resolve()

    # Find matching project directory
    matching_dir = _find_matching_project_dir(claude_projects, project_path)
    if not matching_dir:
        return None

    # Find most recent transcript in that directory
    transcript = _find_most_recent_transcript(matching_dir)
    if not transcript:
        return None

    return str(transcript)


def list_all_projects() -> List[dict]:
    """List all Claude projects with their transcripts.

    Returns project info including both encoded directory names and original paths.
    Perfect for building project selectors and APIs.

    Returns:
        List of project dictionaries with:
        - original_path: The actual project path (e.g., "/Volumes/AliDev/ai-projects/memory")
        - encoded_name: The directory name in ~/.claude/projects (e.g., "-Volumes-AliDev-ai-projects-memory")
        - transcripts: List of transcript filenames with metadata

    Example:
        projects = list_all_projects()
        # Use functional approach in examples too
        list(toolz_map(
            lambda project: print(f"{project['original_path']} -> {project['encoded_name']}\n  Transcripts: {len(project['transcripts'])}"),
            projects
        ))
    """
    claude_projects = Path.home() / ".claude" / "projects"

    if not claude_projects.exists():
        return []

    # Functional pipeline to build project list
    def process_project_dir(project_dir):
        """Process a single project directory functionally."""
        if not project_dir.is_dir():
            return None

        # Get all JSONL files
        jsonl_files = list(project_dir.glob("*.jsonl"))
        if not jsonl_files:
            return None

        # Extract original path from first JSONL file
        original_path = _extract_original_path_from_jsonl(jsonl_files[0])
        if not original_path:
            return None

        # Build transcript info using functional approach
        transcripts = list(toolz_map(_build_transcript_info, jsonl_files))

        # Sort by modification time (most recent first)
        transcripts.sort(key=lambda x: x["modified"], reverse=True)

        return {
            "original_path": original_path,
            "encoded_name": project_dir.name,
            "project_dir": str(project_dir),
            "transcripts": transcripts,
            "latest_transcript": transcripts[0]["path"] if transcripts else None,
        }

    # Apply functional processing pipeline
    project_dirs = claude_projects.iterdir()
    processed_projects = toolz_map(process_project_dir, project_dirs)
    valid_projects = list(toolz_filter(lambda x: x is not None, processed_projects))

    return valid_projects


def find_project_by_original_path(target_path: str | Path) -> Optional[dict]:
    """Find project info by original path.

    Args:
        target_path: Original project path (e.g., "/Volumes/AliDev/ai-projects/memory")

    Returns:
        Project dict with encoded_name, transcripts, etc., or None if not found

    Example:
        project = find_project_by_original_path("/Volumes/AliDev/ai-projects/memory")
        if project:
            print(f"Encoded name: {project['encoded_name']}")
            print(f"Latest transcript: {project['latest_transcript']}")
    """
    target_path = Path(target_path).resolve()
    projects = list_all_projects()

    # Use functional approach to find matching project
    def matches_target_path(project):
        project_path = Path(project["original_path"])
        return target_path == project_path or target_path.is_relative_to(project_path)

    return more_first(toolz_filter(matches_target_path, projects), default=None)


def find_all_transcripts_for_cwd(project_path: Path) -> List[str]:
    """Find ALL transcript files for a project directory.

    Critical for multi-session handling - gets all JSONL files, not just most recent.

    Args:
        project_path: Path to project directory

    Returns:
        List of paths to all transcript files for this project

    Example:
        # Get all sessions for current project
        transcripts = find_all_transcripts_for_cwd(Path.cwd())
        for transcript_path in transcripts:
            timeline = Timeline(Path(transcript_path).parent)
    """
    claude_projects = Path.home() / ".claude" / "projects"

    if not claude_projects.exists():
        return []

    # Normalize the project path
    project_path = project_path.resolve()

    # Find matching project directory
    matching_dir = _find_matching_project_dir(claude_projects, project_path)
    if not matching_dir:
        return []

    # Get ALL JSONL files (not just most recent)
    jsonl_files = list(matching_dir.glob("*.jsonl"))

    # Sort by modification time (most recent first)
    jsonl_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    return [str(f) for f in jsonl_files]


def find_project_by_encoded_name(encoded_name: str) -> Optional[dict]:
    """Find project info by encoded directory name.

    Args:
        encoded_name: Encoded directory name (e.g., "-Volumes-AliDev-ai-projects-memory")

    Returns:
        Project dict with original_path, transcripts, etc., or None if not found

    Example:
        project = find_project_by_encoded_name("-Volumes-AliDev-ai-projects-memory")
        if project:
            print(f"Original path: {project['original_path']}")
            print(f"Number of transcripts: {len(project['transcripts'])}")
    """
    projects = list_all_projects()

    # Use functional approach to find matching project
    def matches_encoded_name(project):
        return project["encoded_name"] == encoded_name

    return more_first(toolz_filter(matches_encoded_name, projects), default=None)


def _find_matching_project_dir(
    claude_projects: Path, target_path: Path
) -> Optional[Path]:
    """Find Claude project directory by checking cwd in JSONL files.

    95/5 approach: Read first line of JSONL to get actual cwd path.
    This handles all edge cases with dashes in original paths.
    """

    def check_project_dir(project_dir):
        """Check if a project directory matches the target path."""
        if not project_dir.is_dir():
            return None

        # Get any JSONL file to check the cwd
        jsonl_files = list(project_dir.glob("*.jsonl"))
        if not jsonl_files:
            return None

        # Extract original path and check if it matches
        original_path = _extract_original_path_from_jsonl(jsonl_files[0])
        if not original_path:
            return None

        cwd = Path(original_path)
        # Check if target path is under this cwd
        if target_path == cwd or target_path.is_relative_to(cwd):
            return project_dir

        return None

    # Use functional approach to find matching directory
    project_dirs = claude_projects.iterdir()
    checked_dirs = toolz_map(check_project_dir, project_dirs)
    matching_dirs = toolz_filter(lambda x: x is not None, checked_dirs)

    return more_first(matching_dirs, default=None)


def _extract_original_path_from_jsonl(jsonl_file: Path) -> Optional[str]:
    """Extract original project path from JSONL file."""
    try:
        with open(jsonl_file, "rb") as f:
            # Find first line with 'cwd' using functional approach
            lines_with_cwd = toolz_filter(
                lambda line: b"cwd" in line and orjson.loads(line).get("cwd"), f
            )
            first_cwd_line = more_first(lines_with_cwd, default=None)

            if first_cwd_line:
                data = orjson.loads(first_cwd_line)
                return data.get("cwd")

    except (orjson.JSONDecodeError, KeyError, ValueError, FileNotFoundError):
        pass

    return None


def _build_transcript_info(jsonl_file: Path) -> dict:
    """Build transcript info dict from JSONL file."""
    stat = jsonl_file.stat()
    return {
        "filename": jsonl_file.name,
        "session_id": jsonl_file.stem,
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "path": str(jsonl_file),
    }


def _find_most_recent_transcript(project_dir: Path) -> Optional[Path]:
    """Find the most recently modified .jsonl file in project directory."""
    jsonl_files = list(project_dir.glob("*.jsonl"))

    if not jsonl_files:
        return None

    # Use max with key instead of manual sorting
    return max(jsonl_files, key=lambda f: f.stat().st_mtime)
