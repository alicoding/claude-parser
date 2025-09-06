"""
Claude Code Timeline - Polars-based implementation following 95/5 principle.

SOLID: Separated into two focused classes:
- DataFrameTimeline: JSONL analysis using Polars (for status, stats, queries)
- GitRestoration: File restoration using pygit2 (for checkout, undo)

95/5: 95% framework code (Polars + pygit2), 5% glue code.
"""

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import polars as pl
import pygit2
import tempfile
import jsonlines
from more_itertools import flatten
import pandas as pd
import pandas as pd
import pandas as pd
import pandas as pd

from ..interfaces import ProjectDiscoveryInterface
from ...infrastructure.discovery import ConfigurableProjectDiscovery


class ClaudeCodeTimeline:
    """SDK-based timeline using conversation domain.

    SOLID: Single responsibility using existing conversation + discovery services.
    SDK: 100% existing SDK, zero custom code.
    """

    def __init__(
        self, project_path: Path, discovery: Optional[ProjectDiscoveryInterface] = None
    ):
        """Initialize with project path and discovery service."""
        self.input_path = project_path.resolve()
        self.discovery = discovery or ConfigurableProjectDiscovery()

        # Use discovery to find Claude Code project
        discovered_project = self.discovery.find_current_project(self.input_path)
        if not discovered_project:
            raise ValueError(
                f"No Claude Code project found for path: {self.input_path}"
            )

        self.claude_project_path = discovered_project

        # Get transcript paths using discovery
        self.transcript_paths = self.discovery.get_project_transcripts(
            self.claude_project_path
        )

        if not self.transcript_paths:
            raise ValueError(
                f"No Claude Code transcripts found for {self.claude_project_path}"
            )

        # Load all conversations using SDK
        print(f"✅ Loaded {len(self.transcript_paths)}/{len(self.transcript_paths)} transcript files")
        self.conversations = load_many(self.transcript_paths)

        # Legacy compatibility: extract tool operations from conversations
        self.tool_operations = self._get_all_tool_operations()

        # Extract project working directory
        self.project_path = self.input_path

        # Git restoration helper (lazy initialization)
        self._git_restoration = None

    def _get_all_tool_operations(self) -> List[Dict]:
        """Extract tool operations from all conversations using SDK."""
        tool_operations = []

        for conversation in self.conversations:
            # Use SDK: conversation.tool_uses extracts all tool operations
            for tool_block in conversation.tool_uses:
                if hasattr(tool_block, 'name') and tool_block.name in ['Write', 'Edit', 'MultiEdit', 'Read']:
                    if hasattr(tool_block, 'input') and hasattr(tool_block.input, 'file_path'):
                        tool_operations.append({
                            'tool_name': tool_block.name,
                            'file_path': tool_block.input.file_path,
                            'uuid': tool_block.id if hasattr(tool_block, 'id') else 'unknown',
                            'sessionId': conversation.session_id or 'unknown',
                            'timestamp': getattr(tool_block, 'timestamp', ''),
                            'tool_input': tool_block.input.__dict__ if hasattr(tool_block.input, '__dict__') else {}
                        })

        return tool_operations

    # True One-Liner SDK Methods

    def get_multi_session_summary(self) -> Dict[str, Any]:
        """One-liner: use our analytics SDK."""
        return {
            "total_sessions": len(self.conversations),
            "total_operations": sum(analyze(conv)["tool_uses"] for conv in self.conversations),
            "sessions": {conv.session_id or "unknown": analyze(conv) for conv in self.conversations}
        }

    def get_status_since_last_user_message(self) -> Dict:
        """One-liner: current session checkpoint + cross-session tool usage."""
        if not self.conversations:
            return {"operations": [], "files_modified": [], "summary": "No conversations found"}

        # One-liner: get last user from current session (newest conversation)
        current = self.conversations[0]
        last_user = current.user_messages[-1] if current.user_messages else None
        if not last_user:
            return {"operations": [], "files_modified": [], "summary": "No user messages found"}

        # One-liner: get operations since checkpoint across all conversations using SDK
        operations = [
            {'tool_name': t.name, 'file_path': getattr(t.input, 'file_path', '')}
            for conv in self.conversations
            for msg in conv.get_messages_between_timestamps(last_user.timestamp, "9999-12-31T23:59:59Z")
            for t in getattr(msg, 'tool_uses', [])
            if hasattr(t, 'name') and t.name in ['Write', 'Edit', 'MultiEdit']
        ]

        files_modified = list(set(op['file_path'] for op in operations))
        return {"operations": operations, "files_modified": files_modified, "summary": f"{len(operations)} operations since last user message"}

    def find_last_user_message(self) -> Optional[Dict]:
        """One-liner: get last user from current session."""
        if not self.conversations: return None
        last_user = self.conversations[0].user_messages[-1] if self.conversations[0].user_messages else None
        return {"timestamp": last_user.timestamp} if last_user else None

    def get_operations_since_last_user_message(self) -> List[Dict]:
        """One-liner: delegate to status method."""
        return self.get_status_since_last_user_message().get("operations", [])

    def get_session_operations(self, session_id: str) -> List[Dict]:
        """One-liner: find conversation by session_id and get tool usage."""
        conv = next((c for c in self.conversations if c.session_id == session_id), None)
        if conv:
            # Removed circular import - ConversationAnalytics imported lazily if needed
            return ConversationAnalytics(conv).get_tool_usage()
        return []

    # File Restoration Methods (pygit2-based)

    def _get_git_restoration(self):
        """Lazy initialize Git restoration helper."""
        if self._git_restoration is None:
            self._git_restoration = GitRestoration(self.tool_operations)
        return self._git_restoration

    def checkout(self, point: str) -> Dict[str, Any]:
        """Checkout repository state at specific point."""
        return self._get_git_restoration().checkout(point)

    def checkout_by_uuid(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Checkout repository state at specific UUID."""
        return self._get_git_restoration().checkout_by_uuid(uuid)

    def get_operation_diff(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get diff for specific operation."""
        return self._get_git_restoration().get_operation_diff(uuid)

    def diff(self, from_point: str, to_point: str) -> Dict:
        """Get diff between two points."""
        return self._get_git_restoration().diff(from_point, to_point)

    def clear_cache(self):
        """Clean up resources."""
        if self._git_restoration:
            self._git_restoration.clear_cache()
