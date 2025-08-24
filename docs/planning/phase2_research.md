# Phase 2 Library Research & Architecture Plan

## Current State Analysis

### Existing Dependencies (Phase 1)
- **orjson**: Fast JSON parsing ✅
- **pydantic v2**: Type validation ✅  
- **pendulum**: Date handling ✅
- **loguru**: Logging ✅
- **rich**: CLI output ✅
- **httpx**: HTTP client ✅

### Phase 2 Requirements
1. **File Watching**: Monitor JSONL files for new messages
2. **Hook Helpers**: Simplify Claude Code hook development
3. **Async Support**: Event-driven architecture

## Library Research Results

### 1. File Watching Library
**Winner: watchfiles** (already in SPECIFICATION.md)

**Why watchfiles?**
- Rust-based (via notify crate) - 10x faster than watchdog
- Cross-platform (Mac, Linux, Windows)
- Built for Python async/await
- Used by FastAPI for hot-reloading
- Handles file rotation/truncation automatically
- Low latency (< 10ms detection)

**Code Example:**
```python
from watchfiles import watch

for changes in watch('/path/to/dir'):
    print(changes)  # Set of (Change, path) tuples
```

### 2. Async/Event System
**Winner: asyncio + blinker** (already mandated)

**Why this combination?**
- asyncio: Standard library, mature, well-documented
- blinker: Simple signals, Flask-tested, minimal boilerplate
- Together: Perfect for event-driven file watching

**Code Example:**
```python
from blinker import signal
import asyncio

# Define signals
new_messages_signal = signal('new-messages')

# Connect handlers
@new_messages_signal.connect
async def handle_new_messages(sender, messages):
    print(f"Got {len(messages)} new messages")
```

### 3. Hook System Architecture
**Winner: Simple decorators + pydantic** (no extra library needed)

**Why no extra library?**
- We already have pydantic for validation
- Python decorators are sufficient for hooks
- Simpler than pluggy/plugins
- Type-safe with pydantic models

## Phase 2 Architecture Design

### Module Structure
```
claude_parser/
├── __init__.py           # Existing
├── conversation.py       # Existing
├── models.py            # Existing  
├── parser.py            # Existing
├── watch/               # NEW - File watching module
│   ├── __init__.py
│   ├── monitor.py       # Core monitoring logic
│   ├── incremental.py   # Incremental parsing
│   └── events.py        # Event signals
└── hooks/               # NEW - Hook helpers
    ├── __init__.py
    ├── types.py         # Hook data models
    ├── io.py            # Input/output helpers
    └── context.py       # Conversation context

```

### Dependency Strategy

**Core Dependencies** (always installed):
- orjson, pydantic, pendulum, loguru

**Optional Dependencies** (extras):
```toml
[project.optional-dependencies]
watch = ["watchfiles>=0.24.0", "blinker>=1.8.0"]
hooks = []  # No extra deps needed, uses core

# Install options:
pip install claude-parser           # Core only
pip install claude-parser[watch]    # With file watching
pip install claude-parser[hooks]    # With hook helpers
pip install claude-parser[all]      # Everything
```

## Implementation Plan

### Phase 2A: Hook Helpers (No new dependencies)
```python
# claude_parser/hooks/__init__.py
from typing import Optional
import sys
import orjson
from pydantic import BaseModel

class HookData(BaseModel):
    """Unified hook data using existing pydantic."""
    hook_type: str
    session_id: str
    transcript_path: str
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    # ... other fields

def hook_input() -> HookData:
    """Parse stdin using existing orjson."""
    data = orjson.loads(sys.stdin.read())
    return HookData(**data)

def exit_success(message: str = ""):
    """Simple exit helper."""
    if message:
        print(message)
    sys.exit(0)

def exit_block(reason: str):
    """Block with reason."""
    print(reason, file=sys.stderr)
    sys.exit(2)
```

### Phase 2B: File Watching (watchfiles + blinker)
```python
# claude_parser/watch/__init__.py
from watchfiles import watch as _watch
from blinker import signal
from pathlib import Path
import orjson

# Signals for events
new_messages = signal('new-messages')
file_rotated = signal('file-rotated')

class ConversationMonitor:
    """Monitor JSONL files for changes."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.last_position = 0
        self.seen_uuids = set()
        
    async def watch(self):
        """Watch for changes using watchfiles."""
        async for changes in _watch(self.filepath):
            new_msgs = self._parse_incremental()
            if new_msgs:
                new_messages.send(self, messages=new_msgs)
    
    def _parse_incremental(self):
        """Parse only new lines using orjson."""
        # Implementation here
        pass
```

## Benefits of This Approach

### 1. **Minimal New Dependencies**
- Phase 2A (hooks): Zero new dependencies
- Phase 2B (watch): Only watchfiles + blinker
- Both are optional extras

### 2. **Leverages Existing Stack**
- orjson for all JSON parsing
- pydantic for all validation
- loguru for all logging
- No duplication

### 3. **True 95/5 Design**
```python
# 95% use case (3 lines)
from claude_parser import watch
watch("transcript.jsonl", callback)

# 5% use case (advanced control)
from claude_parser.watch import ConversationMonitor
monitor = ConversationMonitor("transcript.jsonl")
monitor.signals.connect('new-messages', custom_handler)
await monitor.watch()
```

### 4. **Performance**
- watchfiles: 10x faster than watchdog
- orjson: 10x faster than json
- Incremental parsing: O(new_lines) not O(total_lines)
- Memory efficient: Never reload entire file

### 5. **Compatibility**
- Works with existing Phase 1 code
- Optional extras don't break core
- Clean migration path for users

## Next Steps

1. **Implement hook helpers** (no new deps)
2. **Implement file watching** (watchfiles + blinker)
3. **Write comprehensive tests**
4. **Update documentation**
5. **Release as v0.2.0**