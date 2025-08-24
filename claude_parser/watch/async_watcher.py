"""
Async watcher implementation - Watch Domain.

SOLID Principles:
- SRP: Single responsibility - async file watching
- OCP: Open for extension via callbacks
- LSP: Can substitute for sync watcher interface
- ISP: Focused interface - watch_async only
- DIP: Depends on abstractions (watchfiles library)

95/5 Principle:
- Uses watchfiles.awatch (NOT custom file polling)
- Simple async generator interface
- No manual threading (watchfiles handles it)
"""

from typing import AsyncGenerator, Optional, List, Callable
from pathlib import Path
import asyncio
from watchfiles import awatch, Change
from loguru import logger

from ..domain.conversation import Conversation
from ..infrastructure.message_repository import JsonlMessageRepository
from ..models import Message


class AsyncWatcher:
    """Async file watcher following DDD principles."""
    
    def __init__(self, repository: Optional[JsonlMessageRepository] = None):
        """Initialize with repository dependency injection."""
        self._repository = repository or JsonlMessageRepository()
        self._last_messages: List[Message] = []
        self._last_size: int = 0
    
    async def watch_async(
        self,
        file_path: str | Path,
        message_types: Optional[List[str]] = None,
        debounce: int = 100,
        stop_event: Optional[asyncio.Event] = None
    ) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
        """
        Asynchronously watch a JSONL file for changes.
        
        Uses watchfiles.awatch internally - NO manual threading!
        The Rust backend runs in a separate thread automatically.
        
        Args:
            file_path: Path to JSONL file
            message_types: Optional filter for message types
            debounce: Milliseconds to debounce rapid changes
            stop_event: Optional event to stop watching
            
        Yields:
            Tuple of (full_conversation, new_messages)
        """
        file_path = Path(file_path)
        
        # Wait for file creation if needed
        if not file_path.exists():
            logger.info(f"Waiting for {file_path.name} to be created...")
            async for changes in awatch(str(file_path.parent), stop_event=stop_event):
                if any(str(file_path) in path for _, path in changes):
                    break
        
        # Initialize state
        self._last_messages = []
        self._last_size = 0
        
        # Initial load
        if file_path.exists():
            result = await self._process_file(file_path, message_types, initial=True)
            if result:
                yield result
        
        # Watch for changes - awatch handles threading!
        logger.info(f"Watching {file_path.name} asynchronously...")
        
        async for changes in awatch(
            str(file_path),
            debounce=debounce,
            stop_event=stop_event
        ):
            # Process only modifications
            for change_type, path in changes:
                if change_type == Change.modified:
                    result = await self._process_file(file_path, message_types)
                    if result:
                        yield result
    
    async def _process_file(
        self,
        file_path: Path,
        message_types: Optional[List[str]] = None,
        initial: bool = False
    ) -> Optional[tuple[Conversation, List[Message]]]:
        """Process file changes and return new messages."""
        try:
            # Load messages using repository
            messages = self._repository.load_messages(file_path)
            current_size = file_path.stat().st_size
            
            # Handle file rotation
            if current_size < self._last_size:
                logger.info("File truncated/rotated, reloading from start")
                self._last_messages = []
            
            # Find new messages
            if initial:
                new_messages = messages
            else:
                new_messages = messages[len(self._last_messages):]
            
            # Apply type filter
            if message_types and new_messages:
                new_messages = [
                    msg for msg in new_messages
                    if msg.type.value in message_types
                ]
            
            if new_messages:
                # Create conversation
                metadata = self._repository.get_metadata_from_messages(messages, file_path)
                conv = Conversation(messages, metadata)
                
                # Update state
                self._last_messages = messages
                self._last_size = current_size
                
                return conv, new_messages
                
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return None


# ==========================================
# 95/5 FACTORY FUNCTION (Main API)
# ==========================================

async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None
) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
    """
    Watch a JSONL file asynchronously for changes.
    
    95/5 Principle: Dead simple async API - no threading needed!
    Uses watchfiles which runs Rust code in a separate thread.
    
    Args:
        file_path: Path to JSONL file
        message_types: Optional filter ["user", "assistant", etc]
        stop_event: Optional event to stop watching
        
    Yields:
        (conversation, new_messages) on each change
        
    Example:
        async for conv, new_messages in watch_async("session.jsonl"):
            for msg in new_messages:
                print(f"{msg.type}: {msg.text_content}")
    """
    watcher = AsyncWatcher()
    async for result in watcher.watch_async(file_path, message_types, stop_event=stop_event):
        yield result