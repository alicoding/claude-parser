"""
ProjectFinder micro-component - Find Claude Code projects.

95/5 principle: Simple file system operations, framework handles I/O.
Size: ~18 LOC (LLM-readable in single context)
"""

from pathlib import Path
from typing import Optional, List
from ..core.resources import ResourceManager


class ProjectFinder:
    """Micro-component: Find Claude Code project directories."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources
        self.claude_projects = Path.home() / ".claude" / "projects"

    def find_current_project(self, cwd: Path) -> Optional[Path]:
        """Find project for current directory - simple path matching."""
        if not self.claude_projects.exists():
            return None

        cwd_resolved = cwd.resolve()

        # Check each project directory
        for project_dir in self.claude_projects.iterdir():
            if project_dir.is_dir() and self._has_jsonl_files(project_dir):
                if self._matches_project(project_dir, cwd_resolved):
                    return project_dir
        return None

    def _has_jsonl_files(self, directory: Path) -> bool:
        """Check if directory has JSONL files."""
        return any(f.suffix == '.jsonl' for f in directory.iterdir() if f.is_file())

    def _matches_project(self, project_dir: Path, target_path: Path) -> bool:
        """Check if project matches target path by reading first JSONL."""
        import orjson
        for jsonl_file in project_dir.glob('*.jsonl'):
            try:
                with open(jsonl_file, 'rb') as f:
                    for line in f:
                        if b'cwd' in line:
                            data = orjson.loads(line)
                            if 'cwd' in data:
                                project_cwd = Path(data['cwd']).resolve()
                                return target_path == project_cwd or target_path.is_relative_to(project_cwd)
            except (orjson.JSONDecodeError, OSError):
                continue
        return False
