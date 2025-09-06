"""
Timeline - Real Claude Code JSONL Processing
Handles authentic Claude Code JSONL format with multi-session support.
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

from ...discovery import find_all_transcripts_for_cwd


class RealClaudeTimeline:
    """Process authentic Claude Code JSONL with multi-session support."""

    def __init__(self, project_path: Path):
        """Initialize timeline from Claude Code project path.

        Args:
            project_path: Project directory path (auto-discovers JSONL files)
        """
        # Auto-discover all JSONL files for this project
        transcript_paths = find_all_transcripts_for_cwd(project_path)

        if not transcript_paths:
            raise ValueError(f"No Claude Code transcripts found for {project_path}")

        # Load all JSONL files (multi-session support)
        self.raw_events = []
        for transcript_path in transcript_paths:
            with jsonlines.open(transcript_path) as reader:
                session_events = list(reader)
                self.raw_events.extend(session_events)

        # Extract and process tool operations
        self.tool_operations = self._extract_tool_operations(self.raw_events)

        # Initialize git repository
        self.repo = Repo.init(tempfile.mkdtemp())
        self._setup_git()

        # UUID to commit mapping for navigation
        self._uuid_to_commit = {}
        self._session_to_commit = {}

        # Apply operations chronologically across all sessions
        self._apply_all_operations()

    def _setup_git(self):
        """Configure git repository."""
        config = self.repo.config_writer()
        config.set_value("user", "name", "RealClaudeTimeline").release()
        config.set_value("user", "email", "claude@anthropic.com").release()

    def _extract_tool_operations(self, raw_events: List[Dict]) -> List[Dict]:
        """Extract file tool operations from real Claude Code JSONL.

        Real structure:
        {
          "type": "assistant",
          "message": {
            "content": [
              {
                "type": "tool_use",
                "name": "Edit",
                "input": {"file_path": "...", "old_string": "...", "new_string": "..."}
              }
            ]
          },
          "uuid": "...",
          "sessionId": "...",
          "timestamp": "..."
        }
        """
        operations = []

        for event in raw_events:
            # Skip non-assistant events
            if event.get("type") != "assistant":
                continue

            # Extract tool uses from message content
            message = event.get("message", {})
            content_items = message.get("content", [])

            for content_item in content_items:
                if (content_item.get("type") == "tool_use" and
                    self._is_file_operation(content_item)):

                    # Build operation dict with real Claude structure
                    operation = {
                        "uuid": event.get("uuid"),
                        "sessionId": event.get("sessionId"),
                        "timestamp": event.get("timestamp"),
                        "parentUuid": event.get("parentUuid"),
                        "tool_name": content_item.get("name"),
                        "tool_input": content_item.get("input", {}),
                        "cwd": event.get("cwd", ""),
                    }

                    # Add file_path for compatibility
                    if "file_path" in operation["tool_input"]:
                        operation["file_path"] = operation["tool_input"]["file_path"]

                    operations.append(operation)

        # Sort chronologically across all sessions
        operations.sort(key=lambda op: op.get("timestamp", ""))

        return operations

    def _is_file_operation(self, content_item: Dict) -> bool:
        """Check if content item is a file operation tool."""
        tool_name = content_item.get("name", "")
        return tool_name in ["Write", "Edit", "MultiEdit", "Read"]

    def _apply_all_operations(self):
        """Apply all file operations chronologically."""
        for operation in self.tool_operations:
            self._commit_operation(operation)

    def _commit_operation(self, operation: Dict):
        """Commit a single file operation to git."""
        file_path = operation.get("file_path")
        tool_name = operation.get("tool_name")

        if not file_path or tool_name == "Read":
            # Skip Read operations (they don't modify files)
            return

        # Use just the filename, not full path, for git repo
        file = Path(self.repo.working_dir) / Path(file_path).name
        file.parent.mkdir(parents=True, exist_ok=True)
        tool_input = operation.get("tool_input", {})

        # Handle different tool types
        if tool_name == "Write":
            content = tool_input.get("content", "")
            file.write_text(content)

        elif tool_name in ("Edit", "MultiEdit"):
            if not file.exists():
                file.write_text("")  # Create empty file if doesn't exist

            text = file.read_text()

            # Handle MultiEdit (list of edits)
            if tool_name == "MultiEdit":
                edits = tool_input.get("edits", [])
                for edit in edits:
                    old_str = edit.get("old_string", "")
                    new_str = edit.get("new_string", "")
                    text = text.replace(old_str, new_str, 1)
            else:
                # Handle single Edit
                old_str = tool_input.get("old_string", "")
                new_str = tool_input.get("new_string", "")
                text = text.replace(old_str, new_str, 1)

            file.write_text(text)

        # Commit to git
        try:
            self.repo.index.add([str(file)])
            commit_msg = f"{tool_name} {Path(file_path).name} (Session: {operation.get('sessionId', 'unknown')[:8]})"
            commit = self.repo.index.commit(commit_msg)

            # Map UUID to commit for navigation
            if uuid := operation.get("uuid"):
                self._uuid_to_commit[uuid] = commit.hexsha

            # Track session commits
            session_id = operation.get("sessionId", "unknown")
            if session_id not in self._session_to_commit:
                self._session_to_commit[session_id] = []
            self._session_to_commit[session_id].append(commit.hexsha)

        except Exception as e:
            print(f"Failed to commit {file_path}: {e}")

    # Navigation methods (compatible with existing API)

    @lru_cache(maxsize=128)
    def checkout(self, point: str) -> Dict[str, Any]:
        """Checkout repository state at specific point."""
        if point != "latest":
            try:
                self.repo.git.checkout(point.replace("branch:", ""))
            except GitCommandError:
                # Search commits by UUID or partial hash
                for commit in self.repo.iter_commits():
                    if point in str(commit) or point in self._uuid_to_commit.values():
                        self.repo.git.checkout(commit)
                        break

        return self._get_current_state()

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

    def get_session_operations(self, session_id: str) -> List[Dict]:
        """Get all operations from a specific session."""
        return [op for op in self.tool_operations
                if op.get("sessionId") == session_id]

    def get_multi_session_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions and their operations."""
        sessions = {}

        for operation in self.tool_operations:
            session_id = operation.get("sessionId", "unknown")
            if session_id not in sessions:
                sessions[session_id] = {
                    "operations": 0,
                    "files_modified": set(),
                    "first_timestamp": operation.get("timestamp"),
                    "last_timestamp": operation.get("timestamp"),
                }

            sessions[session_id]["operations"] += 1
            if file_path := operation.get("file_path"):
                sessions[session_id]["files_modified"].add(file_path)

            # Update timestamps
            timestamp = operation.get("timestamp", "")
            if timestamp < sessions[session_id]["first_timestamp"]:
                sessions[session_id]["first_timestamp"] = timestamp
            if timestamp > sessions[session_id]["last_timestamp"]:
                sessions[session_id]["last_timestamp"] = timestamp

        # Convert sets to lists for JSON serialization
        for session_data in sessions.values():
            session_data["files_modified"] = list(session_data["files_modified"])

        return {
            "total_sessions": len(sessions),
            "total_operations": len(self.tool_operations),
            "sessions": sessions
        }

    def _get_current_state(self) -> Dict[str, Any]:
        """Get current repository state."""
        return {
            str(p.relative_to(self.repo.working_dir)): {
                "content": p.read_text(),
                "timestamp": str(self.repo.head.commit.committed_datetime),
            }
            for p in Path(self.repo.working_dir).rglob("*")
            if p.is_file() and ".git" not in str(p)
        }

    def clear_cache(self):
        """Clean up temporary git repository."""
        import shutil
        shutil.rmtree(self.repo.working_dir, ignore_errors=True)

    # Additional methods for compatibility with existing Timeline API

    def query(self, expr: str, limit: int = None) -> List[Dict]:
        """Query operations using JMESPath."""
        data = [
            {
                "uuid": op.get("uuid"),
                "sessionId": op.get("sessionId"),
                "tool_name": op.get("tool_name"),
                "file_path": op.get("file_path"),
                "timestamp": op.get("timestamp"),
            }
            for op in self.tool_operations
        ]
        results = jmespath.search(expr, data) or []
        return results[:limit] if limit else results

    def diff(self, from_point: str, to_point: str) -> Dict:
        """Get diff between two points."""
        return DeepDiff(self.checkout(from_point), self.checkout(to_point)).to_dict()

    def get_operation_diff(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get diff for a specific operation by UUID."""
        # Find the operation
        target_op = None
        for op in self.tool_operations:
            if op.get('uuid', '').startswith(uuid) or op.get('uuid') == uuid:
                target_op = op
                break

        if not target_op:
            return None

        # Skip Read operations (no diff)
        if target_op.get('tool_name') == 'Read':
            return None

        file_path = target_op.get('file_path')
        if not file_path:
            return None

        # Get commit hash for this UUID
        commit_sha = self._uuid_to_commit.get(target_op.get('uuid'))
        if not commit_sha:
            return None

        try:
            # Get the commit and its parent
            commit = self.repo.commit(commit_sha)

            # Get file content before and after
            filename = Path(file_path).name

            # Content after the operation
            self.repo.git.checkout(commit_sha)
            after_file = Path(self.repo.working_dir) / filename
            after_content = after_file.read_text() if after_file.exists() else ""

            # Content before the operation (from parent commit)
            before_content = ""
            if commit.parents:
                parent_commit = commit.parents[0]
                self.repo.git.checkout(parent_commit.hexsha)
                before_file = Path(self.repo.working_dir) / filename
                before_content = before_file.read_text() if before_file.exists() else ""

            # Generate simple line-by-line diff
            before_lines = before_content.splitlines()
            after_lines = after_content.splitlines()

            diff_lines = []
            max_lines = max(len(before_lines), len(after_lines))

            for i in range(max_lines):
                before_line = before_lines[i] if i < len(before_lines) else None
                after_line = after_lines[i] if i < len(after_lines) else None

                if before_line != after_line:
                    if before_line is not None and after_line is not None:
                        # Changed line
                        diff_lines.append(f"- {before_line}")
                        diff_lines.append(f"+ {after_line}")
                    elif before_line is not None:
                        # Deleted line
                        diff_lines.append(f"- {before_line}")
                    elif after_line is not None:
                        # Added line
                        diff_lines.append(f"+ {after_line}")

            # Return to latest state
            self.repo.git.checkout("HEAD")

            return {
                'operation': target_op.get('tool_name'),
                'file_path': file_path,
                'diff': diff_lines
            }

        except Exception as e:
            print(f"Failed to get diff for UUID {uuid}: {e}")
            return None
