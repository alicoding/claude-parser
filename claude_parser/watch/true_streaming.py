"""
TRUE 95/5 JSONL Streaming Implementation with UUID Checkpoints.

Following the pattern alignment principle:
- watchfiles: Tells us WHEN something changed (like inotify)
- aiofiles: Async file I/O without blocking
- orjson: Fast JSON parsing (we already use it everywhere)
- Native UUID: Anthropic's built-in checkpoint system

This is like using Temporal for workflows - the library IS the pattern.
NO BYTE POSITION TRACKING - uses native Anthropic UUIDs.
"""

from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Set

import aiofiles
import orjson
from loguru import logger
from watchfiles import awatch


class StreamingJSONLReader:
    """
    TRUE 95/5 streaming reader for JSONL files using UUID checkpoints.
    
    Handles:
    - UUID-based checkpoint tracking (no byte positions!)
    - File rotation detection
    - Incremental reading (only new messages)
    - Large file support
    """
    
    def __init__(self, filepath: Path | str):
        """Initialize with just a filepath - TRUE 95/5 simplicity."""
        self.filepath = Path(filepath)
        self.processed_uuids: Set[str] = set()
        self.last_uuid: Optional[str] = None
        self.last_inode: Optional[int] = None
    
    def set_checkpoint(self, last_uuid: str) -> None:
        """Set UUID checkpoint for resuming."""
        self.last_uuid = last_uuid
        logger.debug(f"Checkpoint set to UUID: {last_uuid}")
    
    async def get_new_messages(self, after_uuid: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get new messages since last UUID checkpoint.
        
        TRUE 95/5: Simple method that does one thing well.
        Uses native UUID tracking, not byte positions.
        """
        checkpoint = after_uuid or self.last_uuid
        messages = []
        found_checkpoint = checkpoint is None  # If no checkpoint, start from beginning
        
        # Check if file exists
        if not self.filepath.exists():
            return messages
        
        try:
            # Check for file rotation
            stat = self.filepath.stat()
            current_inode = stat.st_ino
            
            if self.last_inode is not None and current_inode != self.last_inode:
                logger.info(f"File rotation detected for {self.filepath}")
                # Reset on rotation
                self.processed_uuids.clear()
                self.last_uuid = None
                found_checkpoint = True  # Start from beginning on rotation
            
            self.last_inode = current_inode
            
            async with aiofiles.open(self.filepath, "rb") as f:
                async for line in f:
                    try:
                        # Parse JSON line
                        data = orjson.loads(line)
                        current_uuid = data.get('uuid')
                        
                        if not current_uuid:
                            logger.warning("Message without UUID found, skipping")
                            continue
                        
                        # Skip already processed
                        if current_uuid in self.processed_uuids:
                            continue
                        
                        # Check if we've found the checkpoint
                        if not found_checkpoint:
                            if current_uuid == checkpoint:
                                found_checkpoint = True
                            continue
                        
                        # Collect new message
                        messages.append(data)
                        self.processed_uuids.add(current_uuid)
                        self.last_uuid = current_uuid
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse line: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading file: {e}")
        
        return messages
    
    def reset(self) -> None:
        """Reset state for fresh reading."""
        self.processed_uuids.clear()
        self.last_uuid = None
        logger.debug(f"Reader reset for {self.filepath}")


async def stream_jsonl_incrementally(
    filepath: Path | str, 
    watch: bool = True,
    after_uuid: Optional[str] = None
) -> AsyncGenerator[List[Dict[str, Any]], None]:
    """
    TRUE 95/5 streaming function with UUID checkpoints.
    
    Just like LlamaIndex.from_documents() or Temporal.workflow(),
    this function does EVERYTHING with minimal config.
    
    Args:
        filepath: Path to JSONL file
        watch: If True, watch for changes. If False, just read once.
        after_uuid: Optional UUID to resume after
        
    Yields:
        List of new messages each time file changes
    """
    reader = StreamingJSONLReader(filepath)
    
    if after_uuid:
        reader.set_checkpoint(after_uuid)
    
    # Initial read
    messages = await reader.get_new_messages()
    if messages:
        yield messages
    
    # Watch for changes if requested
    if watch:
        filepath = Path(filepath)
        async for changes in awatch(str(filepath)):
            messages = await reader.get_new_messages()
            if messages:
                yield messages


async def stream_project_incrementally(
    project_path: str,
    checkpoints: Optional[Dict[str, str]] = None
) -> AsyncGenerator[tuple[str, List[Dict[str, Any]]], None]:
    """
    Stream all JSONL files in a Claude project with UUID checkpoints.
    
    Handles multiple sessions, git branches, sidechains automatically.
    
    Args:
        project_path: Path to project (will find Claude directory)
        checkpoints: Dict of filename -> last_uuid for resuming
        
    Yields:
        (filename, new_messages) for each file with changes
    """
    from ..discovery import find_project_by_original_path
    
    project_info = find_project_by_original_path(project_path)
    if not project_info:
        logger.error(f"Project not found: {project_path}")
        return
    
    project_dir = Path.home() / ".claude" / "projects" / project_info["encoded_name"]
    readers = {}
    checkpoints = checkpoints or {}
    
    # Set up readers for all JSONL files
    for jsonl_file in project_dir.glob("*.jsonl"):
        filename = jsonl_file.name
        readers[filename] = StreamingJSONLReader(jsonl_file)
        
        # Apply checkpoint if available
        if filename in checkpoints:
            readers[filename].set_checkpoint(checkpoints[filename])
    
    # Watch entire directory
    async for changes in awatch(str(project_dir), watch_filter=lambda c, p: p.endswith('.jsonl')):
        for change_type, path in changes:
            filename = Path(path).name
            
            # Create reader if new file appears
            if filename not in readers:
                readers[filename] = StreamingJSONLReader(path)
                if filename in checkpoints:
                    readers[filename].set_checkpoint(checkpoints[filename])
            
            # Get new messages
            messages = await readers[filename].get_new_messages()
            if messages:
                yield filename, messages