"""
Timeline - Ultra minimal using maximum libraries.
Every operation delegates to a library.
Enhanced with UUID-based navigation using Anthropic's native system.
"""

import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import jmespath
import jsonlines
from deepdiff import DeepDiff
from git import Repo
from git.exc import GitCommandError
from more_itertools import flatten


class Timeline:
    """Pure delegation to libraries - almost no custom logic."""

    def __init__(self, jsonl_dir: Path):
        self.events = list(
            flatten(jsonlines.open(f) for f in Path(jsonl_dir).glob("*.jsonl"))
        )
        self.repo = Repo.init(tempfile.mkdtemp())
        self._setup_git()
        # UUID to commit mapping for navigation - initialize before applying events
        self._uuid_to_commit = {}
        self._apply_all()

    def _setup_git(self):
        config = self.repo.config_writer()
        config.set_value("user", "name", "Timeline").release()
        config.set_value("user", "email", "t@c.ai").release()

    def _apply_all(self):
        for e in self.events:
            self._commit_event(e)

    def _commit_event(self, e: Dict):
        if not (path := e.get("file_path")):
            return

        file = Path(self.repo.working_dir) / path
        file.parent.mkdir(parents=True, exist_ok=True)

        # Delegate to pathlib and git
        if e.get("tool_name") == "Write":
            file.write_text(e.get("content", ""))
        elif e.get("tool_name") in ("Edit", "MultiEdit"):
            edits = e.get(
                "edits",
                [
                    {
                        "old_string": e.get("old_string"),
                        "new_string": e.get("new_string"),
                    }
                ],
            )
            if file.exists():
                text = file.read_text()
                for edit in edits:
                    text = text.replace(edit["old_string"], edit["new_string"], 1)
                file.write_text(text)

        self.repo.index.add([str(file)])
        commit = self.repo.index.commit(f"{e.get('tool_name')} {path}")

        # Map UUID to commit for navigation
        if uuid := e.get("uuid"):
            self._uuid_to_commit[uuid] = commit.hexsha

    @lru_cache(maxsize=128)
    def checkout(self, point: str) -> Dict[str, Any]:
        # Delegate to git
        if point != "latest":
            try:
                self.repo.git.checkout(point.replace("branch:", ""))
            except GitCommandError:
                # Search commits
                for c in self.repo.iter_commits():
                    if point in str(c):
                        self.repo.git.checkout(c)
                        break

        # Delegate to pathlib
        return {
            str(p.relative_to(self.repo.working_dir)): {
                "content": p.read_text(),
                "timestamp": str(self.repo.head.commit.committed_datetime),
            }
            for p in Path(self.repo.working_dir).rglob("*")
            if p.is_file() and ".git" not in str(p)
        }

    def branch(self, name: str):
        self.repo.create_head(name)

    def list_branches(self) -> List[str]:
        return [b.name for b in self.repo.branches]

    def merge(self, branch: str, into: str) -> List[str]:
        try:
            self.repo.git.checkout(into)
            self.repo.git.merge(branch)
            return []
        except GitCommandError as e:
            return [str(e)]

    def diff(self, from_point: str, to_point: str) -> Dict:
        return DeepDiff(self.checkout(from_point), self.checkout(to_point)).to_dict()

    def query(self, expr: str, limit: int = None) -> List[Dict]:
        data = [
            {"sha": c.hexsha, "message": c.message, "files": list(c.stats.files.keys())}
            for c in self.repo.iter_commits()
        ]
        results = jmespath.search(expr, data) or []
        return results[:limit] if limit else results

    def clear_cache(self):
        import shutil

        shutil.rmtree(self.repo.working_dir, ignore_errors=True)

    # UUID-based navigation methods

    def checkout_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Checkout repository state at specific UUID."""
        if uuid not in self._uuid_to_commit:
            return None

        commit_sha = self._uuid_to_commit[uuid]
        try:
            self.repo.git.checkout(commit_sha)
            return self._get_current_state()
        except GitCommandError:
            return None

    def get_file_at_uuid(self, file_path: str, uuid: str) -> Optional[str]:
        """Get file content at specific UUID."""
        state = self.checkout_by_uuid(uuid)
        if state and file_path in state:
            return state[file_path]["content"]
        return None

    def get_uuid_sequence_for_file(self, file_path: str) -> List[str]:
        """Get chronological sequence of UUIDs that modified a file."""
        uuids = []
        for event in self.events:
            if event.get("file_path") == file_path and event.get("uuid"):
                uuids.append(event.get("uuid"))
        return uuids

    def navigate_file_steps(
        self, file_path: str, steps: int, from_uuid: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Navigate forward/backward N steps in file's modification history."""
        uuid_sequence = self.get_uuid_sequence_for_file(file_path)

        if not uuid_sequence:
            return None

        if from_uuid is None:
            # Start from beginning
            target_index = steps - 1 if steps > 0 else len(uuid_sequence) + steps
        else:
            try:
                current_index = uuid_sequence.index(from_uuid)
                target_index = current_index + steps
            except ValueError:
                return None

        if 0 <= target_index < len(uuid_sequence):
            target_uuid = uuid_sequence[target_index]
            return {
                "uuid": target_uuid,
                "step": target_index + 1,
                "total_steps": len(uuid_sequence),
                "content": self.get_file_at_uuid(file_path, target_uuid),
            }
        return None

    def get_operation_diff(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get diff showing what changed at a specific UUID."""
        # Find the event for this UUID
        event = None
        for e in self.events:
            if e.get("uuid") == uuid:
                event = e
                break

        if not event or not event.get("file_path"):
            return None

        # Get file sequence and find position
        file_path = event.get("file_path")
        uuid_sequence = self.get_uuid_sequence_for_file(file_path)

        try:
            current_index = uuid_sequence.index(uuid)
        except ValueError:
            return None

        # Get content before and after
        if current_index == 0:
            before_content = ""
        else:
            before_uuid = uuid_sequence[current_index - 1]
            before_content = self.get_file_at_uuid(file_path, before_uuid) or ""

        after_content = self.get_file_at_uuid(file_path, uuid) or ""

        return {
            "uuid": uuid,
            "file_path": file_path,
            "operation": event.get("tool_name"),
            "before": before_content,
            "after": after_content,
            "diff": self._compute_diff(before_content, after_content),
        }

    def _get_current_state(self) -> Dict[str, Any]:
        """Get current repository state (like checkout method)."""
        return {
            str(p.relative_to(self.repo.working_dir)): {
                "content": p.read_text(),
                "timestamp": str(self.repo.head.commit.committed_datetime),
            }
            for p in Path(self.repo.working_dir).rglob("*")
            if p.is_file() and ".git" not in str(p)
        }

    def _compute_diff(self, before: str, after: str) -> List[str]:
        """Compute simple line-by-line diff."""
        import difflib

        before_lines = before.splitlines(keepends=True)
        after_lines = after.splitlines(keepends=True)

        return list(
            difflib.unified_diff(
                before_lines,
                after_lines,
                fromfile="before",
                tofile="after",
                lineterm="",
            )
        )
