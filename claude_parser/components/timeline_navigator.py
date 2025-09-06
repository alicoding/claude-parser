"""
TimelineNavigator micro-component - Navigate timeline by UUID and branches.

95/5 principle: Simple navigation logic, Git framework handles versioning.
Size: ~18 LOC (LLM-readable in single context)
"""

from typing import Dict, List, Optional, Any
from git import Repo
from ..core.resources import ResourceManager


class TimelineNavigator:
    """Micro-component: Navigate timeline using Git operations."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    def checkout_by_uuid(self, repo: Repo, uuid: str, uuid_map: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Checkout timeline by UUID - simple Git checkout."""
        if uuid not in uuid_map:
            return None

        commit_hash = uuid_map[uuid]
        repo.git.checkout(commit_hash)
        return self._get_repo_state(repo)

    def get_file_at_uuid(self, repo: Repo, file_path: str, uuid: str, uuid_map: Dict[str, str]) -> Optional[str]:
        """Get file content at specific UUID - let Git handle versioning."""
        if uuid not in uuid_map:
            return None

        commit_hash = uuid_map[uuid]
        try:
            return repo.git.show(f"{commit_hash}:{file_path}")
        except:
            return None

    def _get_repo_state(self, repo: Repo) -> Dict[str, Any]:
        """Get current repository state - simple file reading."""
        state = {}
        repo_path = repo.working_dir
        for file_path in repo.git.ls_files().split('\n'):
            if file_path:
                full_path = f"{repo_path}/{file_path}"
                try:
                    with open(full_path, 'r') as f:
                        state[file_path] = f.read()
                except:
                    state[file_path] = ""
        return state
