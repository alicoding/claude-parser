# Watch API with UUID Checkpoints

## Overview

The watch domain now uses native Anthropic UUID checkpoints instead of byte position tracking. Every message in Claude JSONL has a unique UUID, providing a natural checkpoint system for resumable watching.

## Key Changes

### 🚫 No More Byte Positions
- **Before**: Used `seek()`, `tell()`, and byte positions
- **After**: Uses native message UUIDs for checkpointing
- **Benefit**: More reliable, handles file rotation, no position drift

### ✅ UUID-Based Resume
- Every message has a `uuid` field
- Clients track last processed UUID
- Resume from any point using `after_uuid`

## API Reference

### Synchronous Watching

```python
from claude_parser.watch import watch

def watch(
    file_path: str,
    callback: Callable[[Conversation, List[Message]], None],
    message_types: Optional[List[str]] = None,
    after_uuid: Optional[str] = None,  # NEW!
) -> None:
    """
    Watch JSONL file for changes with UUID checkpoint support.
    
    Args:
        file_path: Path to JSONL file
        callback: Function called with (full_conversation, new_messages)
        message_types: Optional filter ["user", "assistant", etc.]
        after_uuid: Resume after this UUID (skip all messages before)
    
    Example:
        def on_new(conv, new_msgs):
            print(f"Got {len(new_msgs)} new messages")
            # Track checkpoint
            if new_msgs:
                last_uuid = new_msgs[-1].uuid
                save_checkpoint(last_uuid)
        
        # First run
        watch("session.jsonl", on_new)
        
        # Resume after restart
        last_uuid = load_checkpoint()
        watch("session.jsonl", on_new, after_uuid=last_uuid)
    """
```

### Asynchronous Watching

```python
from claude_parser.watch import watch_async

async def watch_async(
    file_path: str | Path,
    message_types: Optional[List[str]] = None,
    stop_event: Optional[asyncio.Event] = None,
    after_uuid: Optional[str] = None,  # NEW!
) -> AsyncGenerator[tuple[Conversation, List[Message]], None]:
    """
    Asynchronously watch JSONL file with UUID checkpoints.
    
    Args:
        file_path: Path to JSONL file
        message_types: Optional filter for message types
        stop_event: Event to stop watching
        after_uuid: Resume after this UUID
        
    Yields:
        (conversation, new_messages) on each change
        
    Example:
        async def watch_with_checkpoint():
            last_uuid = load_checkpoint()
            
            async for conv, new_messages in watch_async(
                "session.jsonl", 
                after_uuid=last_uuid
            ):
                print(f"New: {len(new_messages)}")
                if new_messages:
                    save_checkpoint(new_messages[-1].uuid)
        
        asyncio.run(watch_with_checkpoint())
    """
```

### Project-Wide Watching

```python
from claude_parser.watch.true_streaming import stream_project_incrementally

async def stream_project_incrementally(
    project_path: str,
    checkpoints: Optional[Dict[str, str]] = None
) -> AsyncGenerator[tuple[str, List[Dict[str, Any]]], None]:
    """
    Watch all JSONL files in a Claude project with UUID checkpoints.
    
    Handles:
    - Multiple sessions in same project
    - Git branches (new JSONL files)
    - Sidechains (parallel explorations)
    - Resume/continue (same file appends)
    
    Args:
        project_path: Path to project directory
        checkpoints: Dict of filename -> last_uuid for resume
        
    Yields:
        (filename, new_messages) for each file with changes
        
    Example:
        # Load checkpoints from persistent storage
        checkpoints = {
            "session1.jsonl": "uuid-123",
            "session2.jsonl": "uuid-456"
        }
        
        async for filename, messages in stream_project_incrementally(
            "/my/project",
            checkpoints=checkpoints
        ):
            print(f"{filename}: {len(messages)} new messages")
            # Update checkpoint for this file
            checkpoints[filename] = messages[-1]["uuid"]
            save_checkpoints(checkpoints)
    """
```

## UUID Checkpoint Classes

### UUIDCheckpointReader

```python
from claude_parser.watch.uuid_tracker import UUIDCheckpointReader

class UUIDCheckpointReader:
    """Single-file UUID checkpoint reader."""
    
    def __init__(self, filepath: Path | str):
        """Initialize with file path."""
        
    def set_checkpoint(self, last_uuid: str) -> None:
        """Set UUID to resume after."""
        
    async def get_new_messages(
        self, after_uuid: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get messages after checkpoint."""
        
    def reset(self) -> None:
        """Clear all tracking state."""
```

### MultiFileUUIDTracker

```python
from claude_parser.watch.uuid_tracker import MultiFileUUIDTracker

class MultiFileUUIDTracker:
    """Track UUID checkpoints across multiple files."""
    
    def set_checkpoints(self, checkpoints: Dict[str, str]) -> None:
        """Set checkpoints for multiple files at once."""
        
    def get_reader(self, filepath: Path | str) -> UUIDCheckpointReader:
        """Get or create reader for a file."""
        
    async def get_new_messages_for_file(
        self, filepath: Path | str
    ) -> List[Dict[str, Any]]:
        """Get new messages for specific file."""
        
    def get_current_checkpoints(self) -> Dict[str, Optional[str]]:
        """Get current checkpoint UUIDs for all files."""
```

## Client Implementation Example

```python
import json
from pathlib import Path
from claude_parser.watch import watch_async

class ConversationWatcher:
    """Example client with persistent checkpoints."""
    
    def __init__(self, checkpoint_file="checkpoints.json"):
        self.checkpoint_file = Path(checkpoint_file)
        self.checkpoints = self._load_checkpoints()
    
    def _load_checkpoints(self) -> dict:
        """Load checkpoints from disk."""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file) as f:
                return json.load(f)
        return {}
    
    def _save_checkpoints(self):
        """Persist checkpoints to disk."""
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoints, f)
    
    async def watch_file(self, file_path: str):
        """Watch a file with persistent checkpoint."""
        file_name = Path(file_path).name
        last_uuid = self.checkpoints.get(file_name)
        
        async for conv, new_messages in watch_async(
            file_path,
            after_uuid=last_uuid
        ):
            if new_messages:
                # Process messages
                await self.process_messages(new_messages)
                
                # Update checkpoint
                self.checkpoints[file_name] = new_messages[-1].uuid
                self._save_checkpoints()
    
    async def process_messages(self, messages):
        """Process new messages (override in subclass)."""
        print(f"Processing {len(messages)} new messages")
```

## Migration Guide

### From Byte Positions to UUIDs

**Before (byte positions):**
```python
class OldReader:
    def __init__(self):
        self.last_position = 0
    
    def read_new(self):
        f.seek(self.last_position)
        # Read from position
        self.last_position = f.tell()
```

**After (UUID checkpoints):**
```python
class NewReader:
    def __init__(self):
        self.last_uuid = None
    
    async def read_new(self):
        messages = await get_new_messages(after_uuid=self.last_uuid)
        if messages:
            self.last_uuid = messages[-1]["uuid"]
```

## Benefits

1. **Reliability**: UUIDs are stable identifiers, no drift
2. **Simplicity**: No seek/tell/position math
3. **Rotation Support**: Handles file rotation gracefully
4. **Native**: Uses Anthropic's built-in UUID system
5. **Stateless**: Readers don't need persistent state
6. **Resumable**: Can resume from any UUID checkpoint

## Performance

- Initial scan: O(n) to find checkpoint UUID
- Subsequent reads: O(n) for new messages only
- Memory: Tracks processed UUIDs to prevent duplicates
- No full file reloading on changes

## Testing

```python
import pytest
from claude_parser.watch.uuid_tracker import UUIDCheckpointReader

@pytest.mark.asyncio
async def test_uuid_checkpoint():
    reader = UUIDCheckpointReader("test.jsonl")
    
    # Read all
    messages = await reader.get_new_messages()
    assert len(messages) > 0
    
    # Set checkpoint
    reader.set_checkpoint(messages[5]["uuid"])
    
    # Read after checkpoint
    remaining = await reader.get_new_messages()
    assert len(remaining) == len(messages) - 6
```