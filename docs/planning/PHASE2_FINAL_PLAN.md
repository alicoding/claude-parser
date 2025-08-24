# Phase 2 Final Implementation Plan (95/5 Compliant)

## ✅ Approved Library Stack

Based on research and 95/5 principle compliance:

| Component | Library | Why | What We Rejected |
|-----------|---------|-----|------------------|
| **File Watching** | watchfiles (SYNC mode) | Rust-based, works synchronously, simple | asyncio (too complex) |
| **Async (if needed)** | anyio | 80% simpler than asyncio, structured concurrency | asyncio (verbose, complex) |
| **Events** | blinker | Simple signals, Flask-tested | RxPY (overcomplicated) |
| **JSON** | orjson (existing) | Already using, fastest | - |
| **Validation** | pydantic (existing) | Already using, type-safe | - |

## 🎯 Key Discovery: Synchronous Watchfiles!

**Watchfiles CAN work synchronously** - no async required!

```python
# THIS WORKS - No async/await needed!
from watchfiles import watch

for changes in watch('file.jsonl'):
    print(changes)  # Simple, clean, synchronous
```

This changes everything - we can deliver the 95/5 experience without ANY async complexity.

## Module 1: Hook Helpers (Zero Async, Zero New Deps)

```python
# claude_parser/hooks/__init__.py
"""
Simple hook helpers - NO async complexity.
"""

import sys
import orjson
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class HookData(BaseModel):
    """Single unified model for ALL hook types."""
    
    # Common fields
    hook_type: str = Field(alias="hook_event_name")
    session_id: str
    transcript_path: str
    
    # Hook-specific fields (all optional)
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    message: Optional[str] = None
    
    def load_conversation(self):
        """Load conversation - synchronous, simple."""
        from ..conversation import Conversation
        return Conversation(self.transcript_path)

# 95% API - 3 functions only
def hook_input() -> HookData:
    """Read and parse hook input - no async."""
    data = orjson.loads(sys.stdin.read())
    return HookData(**data)

def exit_success(message: str = ""):
    """Exit 0 - success."""
    if message:
        print(message)
    sys.exit(0)

def exit_block(reason: str):
    """Exit 2 - block."""
    print(reason, file=sys.stderr)
    sys.exit(2)
```

**Usage (3 lines):**
```python
from claude_parser.hooks import hook_input, exit_success, exit_block

data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

## Module 2: File Watching (Synchronous!)

```python
# claude_parser/watch/__init__.py
"""
File watching - SYNCHRONOUS, no async complexity!
"""

from watchfiles import watch as _watch, Change
from pathlib import Path
from typing import Callable, List, Set
import orjson
from loguru import logger

from ..conversation import Conversation
from ..models import Message, parse_message

class ConversationMonitor:
    """
    Monitor JSONL files - SYNCHRONOUSLY.
    No async, no await, just simple callbacks.
    """
    
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.last_position = 0
        self.seen_uuids: Set[str] = set()
        self.conversation = None
        self._initialize()
    
    def _initialize(self):
        """Load existing file state."""
        if self.filepath.exists():
            self.conversation = Conversation(self.filepath)
            for msg in self.conversation.messages:
                if hasattr(msg, 'uuid') and msg.uuid:
                    self.seen_uuids.add(msg.uuid)
            self.last_position = self.filepath.stat().st_size
    
    def watch(self, callback: Callable):
        """
        Watch file SYNCHRONOUSLY - no async!
        
        This is the 95% use case - simple iteration.
        """
        logger.info(f"Watching {self.filepath}")
        
        # Simple synchronous loop - no async complexity!
        for changes in _watch(self.filepath):
            new_messages = []
            
            for change_type, path in changes:
                if change_type == Change.modified:
                    new_messages.extend(self._parse_new_lines())
                elif change_type == Change.added:
                    # File rotation
                    self.last_position = 0
                    new_messages.extend(self._parse_new_lines())
            
            if new_messages:
                callback(self.conversation, new_messages)
    
    def _parse_new_lines(self) -> List[Message]:
        """Parse only new lines - incremental."""
        new_messages = []
        
        with open(self.filepath, 'rb') as f:
            f.seek(self.last_position)
            new_content = f.read()
            
            for line in new_content.split(b'\n'):
                if not line.strip():
                    continue
                
                try:
                    data = orjson.loads(line)
                    
                    # Deduplication
                    uuid = data.get('uuid')
                    if uuid and uuid in self.seen_uuids:
                        continue
                    
                    msg = parse_message(data)
                    if msg:
                        new_messages.append(msg)
                        if self.conversation:
                            self.conversation._messages.append(msg)
                        if uuid:
                            self.seen_uuids.add(uuid)
                
                except Exception:
                    pass  # Skip malformed lines
            
            self.last_position = f.tell()
        
        return new_messages

# 95% API - One simple function
def watch(filepath: str | Path, callback: Callable) -> None:
    """
    Watch file for changes - SYNCHRONOUSLY.
    
    No async, no await, no complexity.
    
    Example:
        def on_new(conv, messages):
            print(f"Got {len(messages)} new")
        
        watch("file.jsonl", on_new)  # That's it!
    """
    monitor = ConversationMonitor(filepath)
    monitor.watch(callback)
```

## 🚀 Why This Is Better

### NO Async Complexity
```python
# ❌ BAD (asyncio - complex)
import asyncio

async def watch_async():
    async for changes in awatch('file'):
        await process(changes)

asyncio.run(watch_async())

# ✅ GOOD (our approach - simple)
from claude_parser import watch

watch('file', callback)  # Done!
```

### Comparison: Us vs asyncio vs cchooks

| Aspect | Our Approach | asyncio | cchooks |
|--------|-------------|---------|---------|
| **Lines for basic hook** | 3 | 10+ | 15+ |
| **Lines for file watch** | 1 | 8+ | 20+ |
| **Async complexity** | None | High | None |
| **Dependencies** | Minimal | Heavy | Heavy |
| **Learning curve** | 5 min | 2 hours | 30 min |

## Dependencies Update

```toml
[project.optional-dependencies]
# Only watchfiles needed, no async libraries!
watch = ["watchfiles>=0.24.0", "blinker>=1.8.0"]
hooks = []  # Zero new deps

# Note: watchfiles depends on anyio, but we use sync mode
# so users never see async complexity
```

## Real-World Usage

### Your Redis Bridge (15 lines total)
```python
from claude_parser import watch
from your_platform import QueuePattern

def bridge_to_redis(conv, new_messages):
    """Your entire monitoring solution."""
    for msg in new_messages:
        QueuePattern.push(
            f'events:{msg.type.value}',
            {
                'type': msg.type.value,
                'content': msg.text_content,
                'session': conv.session_id,
                'timestamp': msg.timestamp
            }
        )

# One line to replace 513 lines
watch(transcript_path, bridge_to_redis)
```

### Hook Example (3 lines)
```python
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

## Implementation Priority

1. **Hook Helpers First** (Phase 2A)
   - Zero new dependencies
   - Immediate value for hook-v2 project
   - Can ship today

2. **File Watching Second** (Phase 2B)
   - Only adds watchfiles dependency
   - Synchronous mode = no complexity
   - 97% code reduction for memory project

## Success Metrics

- **Simplicity**: No async/await anywhere
- **Lines of code**: 3 lines for 95% use cases
- **Dependencies**: Minimal, optional
- **Performance**: Rust-based watchfiles = fast
- **Learning curve**: < 5 minutes

## Conclusion

By using **synchronous watchfiles** and avoiding asyncio completely, we achieve true 95/5 compliance:
- 95% users: Never see async complexity
- 5% users: Can use anyio if they need it (via watchfiles)
- You: Get 97% code reduction with zero async headaches