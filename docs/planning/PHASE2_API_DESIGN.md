# Phase 2: Complete API Design (95/5 + SOLID/DRY/DDD/TDD)

## 🎯 API Design Goals

1. **95% Use Case**: 3 lines for hooks, 1 line for watching
2. **SOLID**: Each function has ONE responsibility
3. **DRY**: Single HookData model for ALL 8 hook types
4. **DDD**: Clear domain boundaries (hooks vs watch vs parser)
5. **TDD**: Tests define the API contract

---

## 📦 Module Structure (DDD Boundaries)

```
claude_parser/
├── __init__.py          # Parser domain exports (Phase 1)
├── hooks/               # Hooks domain (Phase 2A)
│   ├── __init__.py     # 95% API exports
│   ├── models.py       # HookData model
│   ├── input.py        # hook_input() function
│   ├── exits.py        # exit_* functions
│   └── advanced.py     # 5% API (json_output, etc)
└── watch/              # Watch domain (Phase 2B)
    ├── __init__.py     # 95% API exports
    ├── monitor.py      # ConversationMonitor class
    └── api.py          # watch() function
```

---

## 🔌 Hooks Domain API

### 95% API (3 functions only!)

```python
from claude_parser.hooks import hook_input, exit_block, exit_success

# That's it! These 3 functions handle 95% of use cases
```

#### 1. `hook_input() -> HookData`
```python
def hook_input() -> HookData:
    """Parse hook JSON from stdin.
    
    Works for ALL 8 hook types with zero configuration.
    
    Returns:
        HookData: Parsed hook data with all fields
        
    Exits:
        1: On invalid JSON or missing required fields
        
    Example:
        data = hook_input()  # One line!
    """
```

#### 2. `exit_success(message: str = "") -> NoReturn`
```python
def exit_success(message: str = "") -> NoReturn:
    """Exit with success (code 0).
    
    Args:
        message: Optional stdout message
        
    Example:
        exit_success()  # Silent success
        exit_success("Done")  # With message
    """
```

#### 3. `exit_block(reason: str) -> NoReturn`
```python
def exit_block(reason: str) -> NoReturn:
    """Exit with blocking error (code 2).
    
    Claude processes the reason automatically.
    
    Args:
        reason: Required reason for blocking
        
    Example:
        exit_block("Security violation")
    """
```

#### 4. `exit_error(message: str) -> NoReturn`
```python
def exit_error(message: str) -> NoReturn:
    """Exit with non-blocking error (code 1).
    
    Args:
        message: Error message shown to user
        
    Example:
        exit_error("Warning: deprecated function")
    """
```

### HookData Model (DRY - One Model for ALL)

```python
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

HookEventType = Literal[
    "PreToolUse", "PostToolUse", "Notification",
    "UserPromptSubmit", "Stop", "SubagentStop",
    "PreCompact", "SessionStart"
]

class HookData(BaseModel):
    """Universal hook data model (DRY principle).
    
    Single model handles ALL 8 hook types.
    No subclasses needed (violates DRY).
    """
    
    class Config:
        frozen = True  # Immutable (DDD value object)
        extra = "allow"  # Forward compatibility
    
    # Required fields (ALL hooks have these)
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: HookEventType
    
    # Tool hooks (PreToolUse, PostToolUse)
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None
    
    # Other hook-specific fields
    prompt: Optional[str] = None  # UserPromptSubmit
    message: Optional[str] = None  # Notification
    stop_hook_active: Optional[bool] = None  # Stop/SubagentStop
    trigger: Optional[str] = None  # PreCompact
    custom_instructions: Optional[str] = None  # PreCompact
    source: Optional[str] = None  # SessionStart
    
    @property
    def hook_type(self) -> str:
        """Convenience alias for 95% users."""
        return self.hook_event_name
    
    def load_conversation(self) -> "Conversation":
        """Integration with Parser domain."""
        from claude_parser import load
        return load(self.transcript_path)
```

### Advanced API (5% Use Cases)

```python
from claude_parser.hooks.advanced import json_output

def json_output(
    hook_type: str = None,
    decision: str = None,
    reason: str = None,
    **kwargs
) -> NoReturn:
    """Output JSON for advanced hook control.
    
    Handles hook-specific JSON formats automatically.
    
    Args:
        hook_type: Type of hook (auto-detected if possible)
        decision: Decision (allow/deny/block/ask)
        reason: Reason for decision
        **kwargs: Additional hook-specific fields
        
    Example:
        json_output(
            hook_type="PreToolUse",
            decision="deny",
            reason="Security policy"
        )
    """
```

---

## 👁️ Watch Domain API

### 95% API (1 function!)

```python
from claude_parser.watch import watch

# One line to monitor files!
watch("transcript.jsonl", callback)
```

#### `watch(filepath, callback) -> None`
```python
def watch(
    filepath: Union[str, Path],
    callback: Callable[[Conversation, List[Message]], None]
) -> None:
    """Monitor JSONL file for changes.
    
    95% use case - no configuration needed.
    
    Args:
        filepath: Path to JSONL file
        callback: Function called with (conv, new_messages)
        
    Example:
        def on_new(conv, messages):
            print(f"Got {len(messages)} new")
            
        watch("file.jsonl", on_new)  # That's it!
    """
```

### ConversationMonitor Class (5% Advanced)

```python
from claude_parser.watch import ConversationMonitor

class ConversationMonitor:
    """Advanced monitoring with control.
    
    For 5% who need more than watch().
    """
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.last_position = 0
        self.seen_uuids = set()
    
    def watch(self, callback: Callable) -> None:
        """Start monitoring with callback."""
    
    def stop(self) -> None:
        """Stop monitoring."""
    
    @property
    def is_running(self) -> bool:
        """Check if monitoring active."""
```

---

## 🎯 Complete API Surface (95/5 Test)

### 95% Users Need Only:

```python
# Hooks (3 lines max)
from claude_parser.hooks import hook_input, exit_block, exit_success
data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()

# Watching (1 line)
from claude_parser.watch import watch
watch("file.jsonl", lambda c, m: print(f"New: {len(m)}"))

# Parsing (1 line) - Phase 1
from claude_parser import load
conv = load("session.jsonl")
```

### 5% Advanced Users Can:

```python
# Advanced hooks
from claude_parser.hooks.advanced import json_output
json_output(hook_type="PreToolUse", decision="ask")

# Advanced monitoring
from claude_parser.watch import ConversationMonitor
monitor = ConversationMonitor("file.jsonl")
monitor.watch(callback)
monitor.stop()

# Advanced parsing - Phase 1
from claude_parser.parser import parse_jsonl_streaming
for msg in parse_jsonl_streaming("huge.jsonl"):
    process(msg)
```

---

## ✅ Principle Compliance Check

### SOLID
- ✅ **S**: Each function does ONE thing
  - `hook_input()`: Parse stdin
  - `exit_success()`: Exit 0
  - `exit_block()`: Exit 2
  - `watch()`: Monitor file
  
- ✅ **O**: Open for extension, closed for modification
  - HookData allows extra fields
  - Callbacks for customization
  
- ✅ **L**: All hooks work with same interface
  - Single HookData model
  - No isinstance checks needed
  
- ✅ **I**: Minimal interfaces
  - 3 functions for hooks
  - 1 function for watching
  
- ✅ **D**: Depend on abstractions
  - Callbacks instead of implementations
  - Model interfaces not concrete classes

### DRY
- ✅ Single HookData model (not 8)
- ✅ Single parsing function (hook_input)
- ✅ Reuse Phase 1 parser

### DDD
- ✅ Clear bounded contexts
  - Parser domain (Phase 1)
  - Hooks domain (Phase 2A)
  - Watch domain (Phase 2B)
- ✅ No cross-domain pollution
- ✅ Value objects (frozen models)

### 95/5
- ✅ 3 functions for 95% hooks
- ✅ 1 function for 95% watching
- ✅ Advanced features optional

### TDD
- ✅ Tests define the API
- ✅ Red → Green → Refactor
- ✅ 100% coverage required

---

## 🚀 Implementation Order

1. **HookData model** (models.py)
2. **hook_input()** (input.py)
3. **Exit helpers** (exits.py)
4. **Integration tests**
5. **Advanced features** (advanced.py)
6. **Watch domain** (after hooks complete)

---

## 📝 API Guarantees

1. **No breaking changes** - Only additions
2. **Zero configuration** for 95% use cases
3. **Type hints** on everything
4. **Immutable models** (frozen=True)
5. **Clear error messages** with exit codes
6. **Performance**: < 10ms for hook parsing

This API is **final** and **stable** for Phase 2.