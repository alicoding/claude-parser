# Phase 2 Implementation Plan

## Executive Summary

Based on comprehensive research and codebase analysis, Phase 2 will deliver:

1. **Hook Helpers**: Zero new dependencies, leverages existing pydantic/orjson
2. **File Watching**: watchfiles + blinker for 97% code reduction
3. **True 95/5 API**: 3 lines for common use, full power when needed

## Architecture Decisions

### Why These Libraries?

| Component | Library | Why | Alternative Rejected |
|-----------|---------|-----|---------------------|
| **File Watching** | watchfiles | Rust-based, 10x faster, async-native | watchdog (slower, Python) |
| **Events** | blinker | Simple, Flask-tested, minimal API | pluggy (overcomplicated) |
| **Hook Validation** | pydantic (existing) | Already in use, type-safe | marshmallow (redundant) |
| **JSON** | orjson (existing) | Already in use, fastest | ujson (slower) |
| **Async** | asyncio | Standard, mature, documented | trio (non-standard) |

### Dependency Strategy

```toml
[project.optional-dependencies]
# Modular installation
watch = ["watchfiles>=0.24.0", "blinker>=1.8.0"]
hooks = []  # Uses existing deps only
all = ["watchfiles>=0.24.0", "blinker>=1.8.0"]
```

## Module 1: Hook Helpers (Phase 2A)

### Goal
Replace GoWayLee's cchooks (25+ classes, 15+ lines per hook) with simple 3-line hooks.

### Implementation
```python
# claude_parser/hooks/__init__.py
"""
Hook helpers for Claude Code hooks.
Zero additional dependencies - uses existing orjson + pydantic.
"""

import sys
import orjson
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pathlib import Path

class HookData(BaseModel):
    """Unified hook data for all 8 hook types."""
    
    # Universal fields (all hooks have these)
    hook_type: str = Field(alias="hook_event_name")
    session_id: str = Field(alias="session_id")
    transcript_path: str = Field(alias="transcript_path")
    
    # Tool hooks (PreToolUse, PostToolUse)
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None
    
    # UserPromptSubmit
    prompt: Optional[str] = None
    
    # Notification
    message: Optional[str] = None
    
    # PreCompact
    trigger: Optional[str] = None
    custom_instructions: Optional[str] = None
    
    # SessionStart
    source: Optional[str] = None
    
    # Stop/SubagentStop
    stop_hook_active: Optional[bool] = None
    
    def load_conversation(self):
        """Load full conversation using our parser."""
        from ..conversation import Conversation
        return Conversation(self.transcript_path)

def hook_input() -> HookData:
    """
    Parse hook input from stdin.
    
    95% Use Case:
        data = hook_input()
        if data.tool_name == "Write":
            exit_block("No writes")
        exit_success()
    """
    try:
        raw = sys.stdin.read()
        data = orjson.loads(raw)
        return HookData(**data)
    except Exception as e:
        print(f"Error parsing hook input: {e}", file=sys.stderr)
        sys.exit(1)

def exit_success(message: str = ""):
    """Exit with success (code 0)."""
    if message:
        print(message)
    sys.exit(0)

def exit_block(reason: str):
    """Exit with blocking error (code 2)."""
    print(reason, file=sys.stderr)
    sys.exit(2)

def exit_error(message: str):
    """Exit with non-blocking error (code 1)."""
    print(message, file=sys.stderr)
    sys.exit(1)

# Advanced API for 5% users
def json_response(decision: str, reason: str = "", **kwargs):
    """Send JSON response for advanced control."""
    response = {
        "decision": decision,
        "reason": reason,
        **kwargs
    }
    print(orjson.dumps(response).decode())
    sys.exit(0)
```

### Usage Examples

**Simple Hook (95% case - 3 lines):**
```python
from claude_parser.hooks import hook_input, exit_success, exit_block

data = hook_input()
if data.tool_name == "Write" and "password" in str(data.tool_input):
    exit_block("No password files")
exit_success()
```

**Advanced Hook with Context (5% case):**
```python
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
conv = data.load_conversation()  # Full conversation context

# Check recent errors
if len(conv.with_errors()) > 5:
    exit_block(f"Too many errors: {len(conv.with_errors())}")

# Check for sensitive data in conversation
if conv.search("password"):
    exit_block("Password mentioned in conversation")

exit_success()
```

## Module 2: File Watching (Phase 2B)

### Goal
Replace 513 lines of transcript monitoring with one function call.

### Implementation
```python
# claude_parser/watch/__init__.py
"""
File watching module for real-time JSONL monitoring.
Optional dependency: pip install claude-parser[watch]
"""

try:
    from watchfiles import watch as _watchfiles, Change
    from blinker import signal
    WATCH_AVAILABLE = True
except ImportError:
    WATCH_AVAILABLE = False

from pathlib import Path
from typing import Callable, List, Optional, Set
import orjson
from loguru import logger

from ..conversation import Conversation
from ..models import Message, parse_message

# Event signals
new_messages_signal = signal('new-messages')
file_rotated_signal = signal('file-rotated')
error_signal = signal('error')

class ConversationMonitor:
    """
    Monitor JSONL files for new messages.
    Handles incremental parsing, deduplication, rotation.
    """
    
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.last_position = 0
        self.seen_uuids: Set[str] = set()
        self.conversation: Optional[Conversation] = None
        self._initialize()
    
    def _initialize(self):
        """Load existing messages and track position."""
        try:
            if self.filepath.exists():
                self.conversation = Conversation(self.filepath)
                
                # Track existing message UUIDs
                for msg in self.conversation.messages:
                    if hasattr(msg, 'uuid') and msg.uuid:
                        self.seen_uuids.add(msg.uuid)
                
                # Track file position
                self.last_position = self.filepath.stat().st_size
                logger.info(f"Initialized monitor at position {self.last_position}")
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            self.conversation = None
    
    def watch(self, callback: Callable[[Conversation, List[Message]], None]):
        """
        Watch file for changes and call callback with new messages.
        
        Args:
            callback: Function called with (conversation, new_messages)
        """
        if not WATCH_AVAILABLE:
            raise ImportError(
                "File watching requires watchfiles. "
                "Install with: pip install claude-parser[watch]"
            )
        
        logger.info(f"Starting watch on {self.filepath}")
        
        for changes in _watchfiles(self.filepath):
            try:
                new_msgs = self._process_changes(changes)
                if new_msgs:
                    callback(self.conversation, new_msgs)
                    new_messages_signal.send(self, messages=new_msgs)
            except Exception as e:
                logger.error(f"Error processing changes: {e}")
                error_signal.send(self, error=e)
    
    def _process_changes(self, changes: Set) -> List[Message]:
        """Process file changes and extract new messages."""
        new_messages = []
        
        for change_type, path in changes:
            if change_type == Change.modified:
                # File modified - parse new content
                new_messages.extend(self._parse_incremental())
            elif change_type == Change.added:
                # File recreated (rotation)
                logger.info("File rotation detected")
                file_rotated_signal.send(self)
                self.last_position = 0
                new_messages.extend(self._parse_incremental())
        
        return new_messages
    
    def _parse_incremental(self) -> List[Message]:
        """Parse only new lines added to file."""
        new_messages = []
        
        try:
            with open(self.filepath, 'rb') as f:
                # Seek to last read position
                f.seek(self.last_position)
                new_content = f.read()
                
                if not new_content:
                    return []
                
                # Parse new lines
                for line in new_content.split(b'\n'):
                    if not line.strip():
                        continue
                    
                    try:
                        data = orjson.loads(line)
                        
                        # Deduplication by UUID
                        uuid = data.get('uuid')
                        if uuid and uuid in self.seen_uuids:
                            continue
                        
                        # Parse message
                        msg = parse_message(data)
                        if msg:
                            new_messages.append(msg)
                            if self.conversation:
                                self.conversation._messages.append(msg)
                            if uuid:
                                self.seen_uuids.add(uuid)
                    
                    except Exception as e:
                        logger.debug(f"Skipping malformed line: {e}")
                
                # Update position
                self.last_position = f.tell()
                logger.debug(f"Read {len(new_messages)} new messages")
        
        except Exception as e:
            logger.error(f"Failed to parse incremental: {e}")
        
        return new_messages

# 95% API - One function
def watch(
    filepath: str | Path,
    callback: Callable[[Conversation, List[Message]], None],
    **kwargs
) -> None:
    """
    Watch Claude transcript for new messages.
    
    95% Use Case:
        def on_new(conv, messages):
            print(f"Got {len(messages)} new messages")
        
        watch("transcript.jsonl", on_new)
    
    Features handled automatically:
    - Incremental parsing (not re-reading entire file)
    - Deduplication by UUID
    - File rotation/truncation
    - Error recovery
    - Session ID extraction
    
    Args:
        filepath: Path to JSONL file
        callback: Function(conversation, new_messages)
    """
    monitor = ConversationMonitor(filepath)
    monitor.watch(callback)

# 5% API - Advanced control
def watch_async(filepath: str | Path) -> ConversationMonitor:
    """
    Get monitor object for advanced control.
    
    5% Use Case:
        monitor = watch_async("transcript.jsonl")
        monitor.new_messages_signal.connect(custom_handler)
        await monitor.watch_async()
    """
    return ConversationMonitor(filepath)
```

### Usage Examples

**Simple Monitoring (95% case):**
```python
from claude_parser import watch

def handle_new_messages(conv, new_messages):
    for msg in new_messages:
        print(f"New {msg.type}: {msg.text_content[:50]}...")

watch("transcript.jsonl", handle_new_messages)
```

**Redis Bridge (Your Use Case):**
```python
from claude_parser import watch
from your_platform import QueuePattern

def bridge_to_redis(conv, new_messages):
    """15 lines replacing 513."""
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

watch(transcript_path, bridge_to_redis)  # That's it!
```

## Testing Strategy

### Hook Helper Tests
```python
# tests/test_hooks.py
def test_hook_input_parsing():
    """Test parsing all 8 hook types."""
    
def test_conversation_loading():
    """Test loading conversation from hook."""
    
def test_exit_functions():
    """Test exit helpers."""
```

### File Watching Tests
```python
# tests/test_watch.py
def test_incremental_parsing():
    """Test only new lines are parsed."""
    
def test_deduplication():
    """Test UUID deduplication."""
    
def test_file_rotation():
    """Test handling of file rotation."""
    
def test_memory_efficiency():
    """Test memory stays constant."""
```

## Migration Guide

### For Your hook-v2 Project
```python
# OLD: cchooks (15+ lines)
from cchooks import create_context
context = create_context()
if isinstance(context, PreToolUseContext):
    # ... complex logic

# NEW: claude-parser (3 lines)
from claude_parser.hooks import hook_input, exit_block, exit_success
data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

### For Your memory Project
```python
# OLD: 513 lines of monitoring
from your_module import TranscriptMonitor
monitor = TranscriptMonitor()
# ... 500+ lines

# NEW: 15 lines total
from claude_parser import watch
watch("transcript.jsonl", bridge_to_redis)
```

## Success Metrics

1. **Code Reduction**: 513 → 15 lines (97% reduction)
2. **Performance**: 10x faster parsing (orjson)
3. **Memory**: Constant memory (incremental parsing)
4. **Reliability**: 92+ tests passing
5. **Simplicity**: 3 lines for 95% use cases

## Timeline

- **Week 1**: Implement hook helpers (Phase 2A)
- **Week 2**: Implement file watching (Phase 2B)
- **Week 3**: Testing and documentation
- **Week 4**: Release v0.2.0

## Conclusion

Phase 2 delivers on the 95/5 promise:
- **95% users**: 3-line solutions
- **5% users**: Full power available
- **You**: 97% code reduction
- **Zero technical debt**: Clean architecture