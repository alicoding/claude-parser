"""
File watching implementation using watchfiles framework.

SINGLE RESPONSIBILITY: Detect file changes only.
Framework dependency: ONLY place that imports watchfiles.
"""

import asyncio
from pathlib import Path
from typing import AsyncGenerator

import watchfiles

from ...domain.interfaces.watch_interfaces import FileWatcher
from ..logger_config import logger


class WatchfilesFileWatcher(FileWatcher):
    """File watcher using watchfiles framework - ONLY place with watchfiles dependency."""

    async def watch_for_changes(self, file_path: Path) -> AsyncGenerator[None, None]:
        """Watch file using watchfiles and yield on changes."""

        # Wait for file creation if needed
        if not file_path.exists():
            logger.info(f"Waiting for {file_path.name} to be created...")
            async for changes in watchfiles.awatch(str(file_path.parent)):
                if any(str(file_path) in path for _, path in changes):
                    break

        logger.info(f"Watching {file_path.name} with watchfiles framework...")

        # Watch for file changes
        async for changes in watchfiles.awatch(str(file_path)):
            # Yield when file changes - single responsibility
            yield
