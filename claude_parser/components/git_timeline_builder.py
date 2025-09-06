"""
GitTimelineBuilder micro-component - Build Git-based conversation timelines.

95/5 principle: Simple Git operations, let GitPython framework handle complexity.
Size: ~20 LOC (LLM-readable in single context)
"""

import tempfile
from pathlib import Path
from typing import Dict, List, Any
from git import Repo
from ..core.resources import ResourceManager


class GitTimelineBuilder:
    """Micro-component: Build Git timeline from conversation events."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def create_timeline_repo(self) -> Repo:
        """Create Git repo for timeline - let GitPython handle setup."""
        repo = Repo.init(tempfile.mkdtemp())
        config = repo.config_writer()
        config.set_value("user", "name", "Timeline").release()
        config.set_value("user", "email", "t@c.ai").release()
        return repo

    def commit_event(self, repo: Repo, event: Dict, uuid_map: Dict[str, str]) -> None:
        """Commit single event - simple Git operations."""
        if not (path := event.get("file_path")):
            return

        file = Path(repo.working_dir) / path
        file.parent.mkdir(parents=True, exist_ok=True)

        # Handle different tool types
        if event.get("tool_name") == "Write":
            file.write_text(event.get("content", ""))
        elif event.get("tool_name") in ("Edit", "MultiEdit"):
            if file.exists():
                text = file.read_text()
                edits = event.get("edits", [{"old_string": event.get("old_string"), "new_string": event.get("new_string")}])
                for edit in edits:
                    text = text.replace(edit["old_string"], edit["new_string"], 1)
                file.write_text(text)

        repo.index.add([str(file)])
        commit = repo.index.commit(f"{event.get('tool_name')} {path}")

        if uuid := event.get("uuid"):
            uuid_map[uuid] = commit.hexsha
