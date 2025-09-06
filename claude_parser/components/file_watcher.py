"""
FileWatcher micro-component - Watch JSONL files for changes.

95/5 principle: Simple change detection, watchfiles framework does heavy lifting.
Size: ~18 LOC (LLM-readable in single context)
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional, Tuple, List
import watchfiles
from ..core.resources import ResourceManager
from ..models import Message


class FileWatcher:
    """Micro-component: Watch files and detect changes."""

    def __init__(self, resources: ResourceManager):
        """Initialize with injected resources."""
        self.resources = resources

    async def watch_file_changes(
        self,
        file_path: Path,
        stop_event: Optional[asyncio.Event] = None
    ) -> AsyncGenerator[bool, None]:
        """Watch for file changes - simple wrapper around watchfiles."""
        # Wait for file creation if needed
        if not file_path.exists():
            async for changes in watchfiles.awatch(str(file_path.parent), stop_event=stop_event):
                if any(str(file_path) in path for _, path in changes):
                    yield True
                    break

        # Watch for file modifications
        async for changes in watchfiles.awatch(str(file_path), stop_event=stop_event):
            yield True
