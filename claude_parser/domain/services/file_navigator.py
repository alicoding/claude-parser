"""
File Navigation Service - Pure 95/5 using Anthropic's native UUID system.

No custom building - just filtering and navigation using toolz + existing data.
Follows VSCode/Cursor command pattern with UUID-based state tracking.
"""

from typing import List, Optional, Dict, Any
from functools import lru_cache

from toolz import filter as toolz_filter, groupby

from ...models.content import ToolUseContent


class FileNavigator:
    """
    Navigate file operations using Anthropic's native UUID system.

    Implements VSCode/Cursor patterns:
    - Stack-based navigation with UUIDs as state markers
    - Command pattern where each UUID represents a file operation
    - Immutable state snapshots via git commits
    """

    def __init__(self, tool_operations: List[ToolUseContent]):
        """Initialize with tool operations from conversation."""
        self._operations = tool_operations
        # Cache for performance
        self._file_operations_cache = {}

    @lru_cache(maxsize=64)
    def get_file_operations(self, file_path: str) -> List[ToolUseContent]:
        """Get all operations for a specific file, ordered by UUID."""
        file_ops = list(
            toolz_filter(
                lambda op: self._extract_file_path(op) == file_path, self._operations
            )
        )
        return sorted(file_ops, key=lambda op: op.id)  # UUID ordering

    def get_operations_after_uuid(
        self, start_uuid: str, file_path: Optional[str] = None
    ) -> List[ToolUseContent]:
        """Get all operations after a specific UUID, optionally for one file."""
        operations = self._operations
        if file_path:
            operations = self.get_file_operations(file_path)

        # Find operations after start_uuid
        after_ops = list(
            toolz_filter(lambda op: self._is_uuid_after(op.id, start_uuid), operations)
        )
        return sorted(after_ops, key=lambda op: op.id)

    def get_operations_between_uuids(
        self, start_uuid: str, end_uuid: str, file_path: Optional[str] = None
    ) -> List[ToolUseContent]:
        """Get operations between two UUIDs (exclusive start, inclusive end)."""
        operations = self._operations
        if file_path:
            operations = self.get_file_operations(file_path)

        between_ops = list(
            toolz_filter(
                lambda op: (
                    self._is_uuid_after(op.id, start_uuid)
                    and self._is_uuid_before_or_equal(op.id, end_uuid)
                ),
                operations,
            )
        )
        return sorted(between_ops, key=lambda op: op.id)

    def get_file_navigation_timeline(self, file_path: str) -> List[Dict[str, Any]]:
        """Get chronological timeline of operations for a file."""
        operations = self.get_file_operations(file_path)

        timeline = []
        for i, op in enumerate(operations):
            timeline.append(
                {
                    "step": i + 1,
                    "uuid": op.id,
                    "operation": op.name,  # Edit, Write, MultiEdit
                    "input": op.input,
                    "can_undo_to": i > 0,
                    "can_redo_from": i < len(operations) - 1,
                }
            )
        return timeline

    def get_modified_files_after_uuid(self, start_uuid: str) -> Dict[str, int]:
        """Get all files modified after UUID with operation count."""
        after_ops = self.get_operations_after_uuid(start_uuid)

        # Group by file path and count operations
        file_groups = groupby(self._extract_file_path, after_ops)
        return {file_path: len(list(ops)) for file_path, ops in file_groups.items()}

    def get_operation_at_step(
        self, file_path: str, step: int
    ) -> Optional[ToolUseContent]:
        """Get operation at specific step number (1-indexed) for a file."""
        operations = self.get_file_operations(file_path)
        if 1 <= step <= len(operations):
            return operations[step - 1]
        return None

    def get_uuid_at_step(self, file_path: str, step: int) -> Optional[str]:
        """Get UUID at specific step number for a file."""
        operation = self.get_operation_at_step(file_path, step)
        return operation.id if operation else None

    def find_step_for_uuid(self, file_path: str, target_uuid: str) -> Optional[int]:
        """Find step number (1-indexed) for a specific UUID in file history."""
        operations = self.get_file_operations(file_path)
        for i, op in enumerate(operations):
            if op.id == target_uuid:
                return i + 1
        return None

    def get_navigation_context(
        self, file_path: str, current_uuid: str
    ) -> Dict[str, Any]:
        """Get navigation context (like VSCode's back/forward state)."""
        operations = self.get_file_operations(file_path)
        current_step = self.find_step_for_uuid(file_path, current_uuid)

        if not current_step:
            return {"error": "UUID not found in file history"}

        return {
            "file_path": file_path,
            "current_step": current_step,
            "current_uuid": current_uuid,
            "total_steps": len(operations),
            "can_go_back": current_step > 1,
            "can_go_forward": current_step < len(operations),
            "previous_uuid": operations[current_step - 2].id
            if current_step > 1
            else None,
            "next_uuid": operations[current_step].id
            if current_step < len(operations)
            else None,
        }

    # Helper methods

    def _extract_file_path(self, operation: ToolUseContent) -> Optional[str]:
        """Extract file path from tool operation input."""
        if hasattr(operation, "input") and isinstance(operation.input, dict):
            return operation.input.get("file_path")
        return None

    def _is_uuid_after(self, uuid_a: str, uuid_b: str) -> bool:
        """Check if uuid_a comes after uuid_b (simple string comparison for now)."""
        return uuid_a > uuid_b

    def _is_uuid_before_or_equal(self, uuid_a: str, uuid_b: str) -> bool:
        """Check if uuid_a comes before or equals uuid_b."""
        return uuid_a <= uuid_b

    # Bulk operations for performance

    def get_all_file_timelines(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get navigation timelines for all files."""
        # Group operations by file
        file_groups = groupby(self._extract_file_path, self._operations)

        timelines = {}
        for file_path, ops in file_groups.items():
            if file_path:  # Skip operations without file_path
                timelines[file_path] = self.get_file_navigation_timeline(file_path)

        return timelines

    def get_conversation_file_summary(self) -> Dict[str, Any]:
        """Get overview of all file operations in conversation."""
        file_groups = groupby(self._extract_file_path, self._operations)

        summary = {
            "total_operations": len(self._operations),
            "files_modified": 0,
            "file_details": {},
        }

        for file_path, ops in file_groups.items():
            if file_path:
                ops_list = list(ops)
                summary["files_modified"] += 1
                summary["file_details"][file_path] = {
                    "operations_count": len(ops_list),
                    "first_uuid": ops_list[0].id if ops_list else None,
                    "last_uuid": ops_list[-1].id if ops_list else None,
                    "operation_types": list(set(op.name for op in ops_list)),
                }

        return summary
