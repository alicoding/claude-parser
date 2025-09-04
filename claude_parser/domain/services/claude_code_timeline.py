"""
Claude Code Timeline - Specialized Timeline for Claude Code JSONL format.

Key differences from Timeline:
- Handles Claude Code JSONL structure (nested tool_use in message.content)
- Multi-session support
- Creates files from operations (Timeline assumes files exist)
- UUID-to-commit mapping for navigation
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

from ...discovery import find_all_transcripts_for_cwd


class ClaudeCodeTimeline:
    """Timeline specialized for Claude Code JSONL format."""

    def __init__(self, project_path: Path):
        """Initialize from Claude Code project path."""
        self.project_path = project_path.resolve()

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

        # Extract and process tool operations (with project filtering)
        self.tool_operations = self._extract_tool_operations(self.raw_events)

        # Initialize git repository
        self.repo = Repo.init(tempfile.mkdtemp())
        self._setup_git()

        # UUID to commit mapping for navigation
        self._uuid_to_commit = {}

        # Apply operations chronologically across all sessions
        self._apply_all_operations()

    def _setup_git(self):
        """Configure git repository."""
        config = self.repo.config_writer()
        config.set_value("user", "name", "ClaudeCodeTimeline").release()
        config.set_value("user", "email", "claude@anthropic.com").release()

    def _extract_tool_operations(self, raw_events: List[Dict]) -> List[Dict]:
        """Extract file tool operations from Claude Code JSONL format."""
        operations = []

        for event in raw_events:
            # Skip non-assistant events
            if event.get("type") != "assistant":
                continue

            # Extract tool uses from message content
            message = event.get("message", {})
            content_items = message.get("content", [])

            for content_item in content_items:
                if content_item.get("type") == "tool_use" and self._is_file_operation(
                    content_item
                ):
                    # Build operation dict
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

                    # Filter by project: only include operations on files within this project
                    if self._is_operation_in_project(operation):
                        operations.append(operation)

        # Sort chronologically across all sessions
        operations.sort(key=lambda op: op.get("timestamp", ""))

        return operations

    def _is_file_operation(self, content_item: Dict) -> bool:
        """Check if content item is a file operation tool."""
        tool_name = content_item.get("name", "")
        return tool_name in ["Write", "Edit", "MultiEdit", "Read"]

    def _is_operation_in_project(self, operation: Dict) -> bool:
        """Check if operation is within the current project."""
        file_path = operation.get("file_path")
        if not file_path:
            return False

        try:
            # Convert file_path to absolute path
            file_abs_path = Path(file_path).resolve()

            # Check if file is within project directory
            return file_abs_path.is_relative_to(self.project_path)
        except (ValueError, OSError):
            # If path resolution fails, fall back to string comparison
            return str(self.project_path) in file_path

    def _apply_all_operations(self):
        """Apply all file operations chronologically to build complete file history."""
        # Group operations by file to handle initialization properly
        files_seen = set()

        for operation in self.tool_operations:
            file_path = operation.get("file_path")
            tool_name = operation.get("tool_name")

            # For the first Edit operation on a file (no prior Write),
            # create an initial commit with the old_string content
            if (
                file_path
                and file_path not in files_seen
                and tool_name in ("Edit", "MultiEdit")
            ):
                self._create_initial_state(operation)
                files_seen.add(file_path)

            self._commit_operation(operation)

            if file_path and tool_name != "Read":
                files_seen.add(file_path)

    def _create_initial_state(self, operation: Dict):
        """Create initial file state from the old_string of the first Edit operation."""
        file_path = operation.get("file_path")
        tool_name = operation.get("tool_name")
        tool_input = operation.get("tool_input", {})

        if not file_path:
            return

        file = Path(self.repo.working_dir) / Path(file_path).name
        file.parent.mkdir(parents=True, exist_ok=True)

        # Get the original content from the old_string
        if tool_name == "Edit":
            old_str = tool_input.get("old_string", "")
            if old_str:
                file.write_text(old_str)
                # Commit the initial state
                try:
                    self.repo.index.add([str(file)])
                    commit = self.repo.index.commit(
                        f"Initial state of {Path(file_path).name}"
                    )
                    print(
                        f"Created initial state for {file.name} ({len(old_str)} chars)"
                    )
                except Exception as e:
                    print(f"Failed to commit initial state for {file_path}: {e}")
        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            if edits:
                old_str = edits[0].get("old_string", "")
                if old_str:
                    file.write_text(old_str)
                    # Commit the initial state
                    try:
                        self.repo.index.add([str(file)])
                        commit = self.repo.index.commit(
                            f"Initial state of {Path(file_path).name}"
                        )
                        print(
                            f"Created initial state for {file.name} from MultiEdit ({len(old_str)} chars)"
                        )
                    except Exception as e:
                        print(f"Failed to commit initial state for {file_path}: {e}")

    def _commit_operation(self, operation: Dict):
        """Commit a single file operation to git."""
        file_path = operation.get("file_path")
        tool_name = operation.get("tool_name")

        if not file_path or tool_name == "Read":
            return

        # Use just the filename, not full path, for git repo
        file = Path(self.repo.working_dir) / Path(file_path).name
        file.parent.mkdir(parents=True, exist_ok=True)
        tool_input = operation.get("tool_input", {})

        # File initialization is now handled in _create_initial_state

        # Handle different tool types
        if tool_name == "Write":
            content = tool_input.get("content", "")
            file.write_text(content)

        elif tool_name in ("Edit", "MultiEdit"):
            if not file.exists():
                file.write_text("")  # Create empty file if doesn't exist

            text = file.read_text()
            original_text = text  # Store original for debugging

            # Handle MultiEdit (list of edits)
            if tool_name == "MultiEdit":
                edits = tool_input.get("edits", [])
                for edit in edits:
                    old_str = edit.get("old_string", "")
                    new_str = edit.get("new_string", "")
                    if old_str in text:
                        text = text.replace(old_str, new_str, 1)
            else:
                # Handle single Edit
                old_str = tool_input.get("old_string", "")
                new_str = tool_input.get("new_string", "")
                if old_str in text:
                    text = text.replace(old_str, new_str, 1)

            # Always write the text (even if unchanged) to ensure git tracking
            file.write_text(text)

            # Debug info: log if edit didn't change anything
            if text == original_text:
                print(
                    f"Warning: Edit operation {operation.get('uuid', '')[:8]} made no changes to {file_path}"
                )

        # Commit to git
        try:
            self.repo.index.add([str(file)])
            commit_msg = f"{tool_name} {Path(file_path).name} (Session: {operation.get('sessionId', 'unknown')[:8]})"
            commit = self.repo.index.commit(commit_msg)

            # Map UUID to commit for navigation
            if uuid := operation.get("uuid"):
                self._uuid_to_commit[uuid] = commit.hexsha

        except Exception as e:
            print(f"Failed to commit {file_path}: {e}")

    # Timeline-compatible API methods

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
        # Find full UUID if partial UUID provided
        full_uuid = None
        if uuid in self._uuid_to_commit:
            full_uuid = uuid
        else:
            # Search for partial UUID match
            for stored_uuid in self._uuid_to_commit.keys():
                if stored_uuid.startswith(uuid):
                    full_uuid = stored_uuid
                    break

        if not full_uuid:
            return None

        commit_sha = self._uuid_to_commit[full_uuid]
        try:
            self.repo.git.checkout(commit_sha)
            return self._get_current_state()
        except GitCommandError:
            return None

    def get_operation_diff(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get diff for a specific operation by UUID."""
        # Find the operation
        target_op = None
        for op in self.tool_operations:
            if op.get("uuid", "").startswith(uuid) or op.get("uuid") == uuid:
                target_op = op
                break

        if not target_op:
            return None

        # Skip Read operations (no diff)
        if target_op.get("tool_name") == "Read":
            return None

        file_path = target_op.get("file_path")
        if not file_path:
            return None

        tool_name = target_op.get("tool_name")
        tool_input = target_op.get("tool_input", {})

        # Generate diff from operation data directly
        import difflib

        filename = Path(file_path).name

        if tool_name == "Write":
            # For Write operations, show the content being written
            content = tool_input.get("content", "")
            diff_lines = [
                f"--- /dev/null",
                f"+++ b/{filename}",
                f"@@ -0,0 +1,{len(content.splitlines())} @@",
            ]
            for line in content.splitlines():
                diff_lines.append(f"+{line}")

        elif tool_name in ("Edit", "MultiEdit"):
            # For Edit operations, show the intended change from the operation data
            if tool_name == "MultiEdit":
                # For MultiEdit, combine all changes
                before_content = ""
                after_content = ""
                edits = tool_input.get("edits", [])
                if edits:
                    # Use first edit's old_string as base
                    before_content = edits[0].get("old_string", "")
                    after_content = before_content
                    for edit in edits:
                        old_str = edit.get("old_string", "")
                        new_str = edit.get("new_string", "")
                        after_content = after_content.replace(old_str, new_str, 1)
                else:
                    diff_lines = ["No edits found in MultiEdit operation"]
            else:
                # Single Edit operation
                before_content = tool_input.get("old_string", "")
                after_content = tool_input.get("new_string", "")

            # Generate unified diff from the operation data
            if before_content or after_content:
                before_lines = before_content.splitlines(keepends=True)
                after_lines = after_content.splitlines(keepends=True)

                diff_lines = list(
                    difflib.unified_diff(
                        before_lines,
                        after_lines,
                        fromfile=f"a/{filename}",
                        tofile=f"b/{filename}",
                        lineterm="",
                    )
                )
            else:
                diff_lines = ["No content changes found in operation data"]
        else:
            diff_lines = [f"Unsupported operation type: {tool_name}"]

        return {"operation": tool_name, "file_path": file_path, "diff": diff_lines}

    def get_session_operations(self, session_id: str) -> List[Dict]:
        """Get all operations from a specific session."""
        return [op for op in self.tool_operations if op.get("sessionId") == session_id]

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
            "sessions": sessions,
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
