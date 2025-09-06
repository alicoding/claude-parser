#!/usr/bin/env python3
"""
Robust timeline restoration that handles corrupted JSONL files.
"""

import json
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import jmespath
from deepdiff import DeepDiff
from git import Repo
from git.exc import GitCommandError
from more_itertools import flatten


def robust_jsonl_load(file_path: Path) -> List[Dict]:
    """Load JSONL with error handling for corrupted lines."""
    events = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                events.append(event)
            except json.JSONDecodeError as e:
                print(f"Skipping corrupted line {line_num} in {file_path.name}: {e}")
                continue
    return events


class RobustClaudeCodeTimeline:
    """Timeline with robust JSONL handling."""

    def __init__(self, project_path: Path):
        """Initialize from Claude Code project path."""
        self.project_path = project_path.resolve()

        # Auto-discover all JSONL files for this project
        transcript_dir = Path("/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser")
        transcript_paths = list(transcript_dir.glob("*.jsonl"))

        if not transcript_paths:
            raise ValueError(f"No Claude Code transcripts found in {transcript_dir}")

        # Load all JSONL files with error handling
        self.raw_events = []
        for transcript_path in transcript_paths:
            print(f"Loading {transcript_path.name}...")
            session_events = robust_jsonl_load(transcript_path)
            print(f"  Loaded {len(session_events)} events")
            self.raw_events.extend(session_events)

        print(f"Total events loaded: {len(self.raw_events)}")

        # Extract and process tool operations (with project filtering)
        self.tool_operations = self._extract_tool_operations(self.raw_events)
        print(f"Tool operations found: {len(self.tool_operations)}")

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
            print(f"UUID {uuid} not found in timeline")
            return None

        commit_sha = self._uuid_to_commit[full_uuid]
        try:
            self.repo.git.checkout(commit_sha)
            return self._get_current_state()
        except GitCommandError as e:
            print(f"Failed to checkout commit {commit_sha}: {e}")
            return None

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


def main():
    """Main restoration function."""
    # Initialize timeline for current project
    project_path = Path('/Volumes/AliDev/ai-projects/claude-parser')
    print(f'Initializing timeline for project: {project_path}')

    try:
        timeline = RobustClaudeCodeTimeline(project_path)
        print(f'Timeline initialized with {len(timeline.tool_operations)} operations')

        # Restore to the UUID right before I deleted components
        target_uuid = 'fb91c0c0-d553-4615-9fa8-a2387279be83'
        print(f'Restoring to UUID: {target_uuid}')

        # Get the state at that UUID
        state = timeline.checkout_by_uuid(target_uuid)

        if state:
            print(f'Successfully restored state with {len(state)} files')

            # Look for components-related files
            components_files = []
            for filename, file_data in state.items():
                if any(keyword in filename.lower() or keyword in file_data['content'].lower()[:1000]
                       for keyword in ['components', 'token_counter', 'file_loader']):
                    components_files.append(filename)

            if components_files:
                print(f'Found {len(components_files)} component-related files:')
                for filename in components_files:
                    print(f'  - {filename}')

                    # Write back to the actual project directory
                    target_file = project_path / filename
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    with open(target_file, 'w') as f:
                        f.write(state[filename]['content'])
                    print(f'    Restored to: {target_file}')
            else:
                print('No components-related files found in the restored state.')
                print('Available files:')
                for filename in sorted(state.keys())[:20]:  # Show first 20 files
                    print(f'  - {filename}')
                if len(state) > 20:
                    print(f'  ... and {len(state)-20} more files')
        else:
            print('Failed to restore from UUID')
            print('Available UUIDs in timeline:')
            for uuid in list(timeline._uuid_to_commit.keys())[:10]:
                print(f'  - {uuid}')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
