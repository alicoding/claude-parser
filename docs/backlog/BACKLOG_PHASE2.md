# Claude Parser SDK - Phase 2 Backlog (SOLID/DRY/DDD/TDD Compliant)

## 📋 Required Reading Before Starting
1. **PHASE2_SEQUENTIAL_PLAN.md** - The execution order (MUST follow)
2. **ZERO_DEBT_CHECKLIST.md** - Run after EVERY commit
3. **CCHOOKS_COMPARISON.md** - Features we must match/exceed
4. **docs/hooks.md** - Official Claude Code hook specification

## 🎯 Zero Compromise Development
1. Each task follows SOLID/DRY/DDD/TDD principles strictly
2. 95/5 API is defined upfront - no ambiguity  
3. Libraries are mandated - no reinventing wheels
4. Tests are written FIRST (TDD) - no exceptions
5. If it violates any principle, it gets marked 🔄 and reworked
6. **ZERO technical debt tolerance** (no TODO/FIXME/HACK)

## Phase 2 Epic: Hook Helpers & File Watching

### EPIC-005: Hook Helpers (Zero New Dependencies)
**Goal**: Replace cchooks' 25+ classes with 3 functions following 95/5 principle
**Principles**:
- **S**ingle Responsibility: Each function does ONE thing
- **O**pen/Closed: Extensible via HookData, not modification
- **L**iskov: All hooks work with same interface
- **I**nterface Segregation: Minimal API surface (3 functions)
- **D**ependency Inversion: Depend on abstractions (HookData)
- **DRY**: Single source of truth for hook parsing
- **DDD**: HookData is the domain model

#### TASK-012: Hook Input Parser
**Assigned Libraries**: orjson (existing), pydantic (existing)
**95% API Must Work**:
```python
from claude_parser.hooks import hook_input

data = hook_input()  # ONE function, ALL 8 hook types
print(data.hook_type)  # Works for ANY hook
```

**Success Criteria**:
- [ ] Single `HookData` model handles ALL 8 hook types (DRY)
- [ ] Uses pydantic BaseModel with field aliases (no manual parsing)
- [ ] All fields are Optional except core 3 (session_id, transcript_path, hook_type)
- [ ] NO isinstance checks needed by users (Liskov Substitution)
- [ ] NO separate classes per hook type (violates DRY)
- [ ] Parses stdin using orjson.loads() ONLY

**Anti-patterns to AVOID**:
```python
# ❌ WRONG - Violates DRY (multiple classes)
class PreToolUseData(BaseModel): ...
class PostToolUseData(BaseModel): ...

# ❌ WRONG - Violates 95/5 (too complex)
context = create_context()
if isinstance(context, PreToolUseContext): ...

# ❌ WRONG - Violates SRP (doing too much)
def hook_input():
    data = parse()
    validate()
    transform()
    log()  # Too many responsibilities
```

**Correct Implementation**:
```python
# ✅ RIGHT - Single model, single responsibility
class HookData(BaseModel):
    """Universal hook data - DRY principle."""
    # Core fields (ALL hooks have these - no aliases needed!)
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: str
    
    # Tool hooks (PreToolUse, PostToolUse)
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None  # PostToolUse only
    
    # Other hook-specific fields
    prompt: Optional[str] = None  # UserPromptSubmit
    message: Optional[str] = None  # Notification
    stop_hook_active: Optional[bool] = None  # Stop, SubagentStop
    trigger: Optional[str] = None  # PreCompact
    custom_instructions: Optional[str] = None  # PreCompact
    source: Optional[str] = None  # SessionStart
    
    @property
    def hook_type(self) -> str:
        """Alias for hook_event_name - 95/5 convenience."""
        return self.hook_event_name

def hook_input() -> HookData:
    """Parse stdin - Single Responsibility."""
    return HookData(**orjson.loads(sys.stdin.read()))
```

**Verification**:
```bash
# Must work for ALL 8 hook types with SAME code
echo '{"hook_event_name": "PreToolUse", ...}' | python test_hook.py
echo '{"hook_event_name": "PostToolUse", ...}' | python test_hook.py
echo '{"hook_event_name": "Notification", ...}' | python test_hook.py
# All use SAME hook_input() function
```

#### TASK-013: Exit Helpers + Advanced Methods
**Assigned Libraries**: sys (stdlib only)
**95% API Must Work**:
```python
from claude_parser.hooks import exit_success, exit_block

exit_success()  # Exit 0
exit_block("reason")  # Exit 2 with stderr
```

**5% API (Advanced Hook-Specific Methods)**:
```python
# Optional convenience methods that generate correct JSON
from claude_parser.hooks import advanced

# PreToolUse specific
advanced.allow(reason="Auto-approved")
advanced.deny(reason="Security violation")
advanced.ask()  # Ask user for permission

# UserPromptSubmit specific
advanced.add_context("Additional context here")

# Stop/SubagentStop specific
advanced.prevent(reason="Must continue processing")
```

**Success Criteria**:
- [ ] Basic exits: `exit_success()`, `exit_block()`, `exit_error()`
- [ ] Each basic function ≤ 3 lines (95/5 simplicity)
- [ ] Advanced methods generate correct JSON for each hook type
- [ ] Advanced methods are OPTIONAL (not required for 95% use)
- [ ] NO JSON in basic exits (separation of concerns)

**Anti-patterns to AVOID**:
```python
# ❌ WRONG - Violates SRP (doing too much)
def exit_success(message="", log=False, notify=False): ...

# ❌ WRONG - Violates 95/5 (too complex)
def exit_with_options(code, message, stream, format): ...
```

**Verification**:
```bash
pytest tests/test_hook_exits.py -v
# Tests: exit codes, stdout/stderr routing, message handling
```

#### TASK-014: Advanced JSON Output (5% API)
**Assigned Libraries**: orjson (existing)
**5% API (Advanced Users Only)**:
```python
from claude_parser.hooks import json_output

# For users who need JSON responses (PreToolUse example)
json_output(
    decision="deny",  # or "allow", "ask" for PreToolUse
    reason="Security violation",
    hook_type="PreToolUse"  # Auto-determines format
)
```

**Success Criteria**:
- [ ] Separate function from basic exits (Interface Segregation)
- [ ] Supports ALL JSON formats from official docs:
  - [ ] PreToolUse: `hookSpecificOutput` with `permissionDecision`
  - [ ] PostToolUse: `decision` and `reason`
  - [ ] UserPromptSubmit: `decision` and `hookSpecificOutput.additionalContext`
  - [ ] Stop/SubagentStop: `decision` and `reason`
  - [ ] SessionStart: `hookSpecificOutput.additionalContext`
- [ ] Auto-detects hook type and uses correct format
- [ ] Handles deprecated fields (`approve` → `allow`, `block` → `deny`)
- [ ] Always exits with code 0 after JSON output

**Critical Compatibility**:
```python
def json_output(decision=None, reason=None, hook_type=None, **kwargs):
    """Smart JSON output that matches Claude's expectations."""
    # PreToolUse uses different structure!
    if hook_type == "PreToolUse":
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,  # "allow", "deny", "ask"
                "permissionDecisionReason": reason
            }
        }
    else:
        # Other hooks use simpler format
        output = {"decision": decision, "reason": reason}
    
    print(orjson.dumps(output).decode())
    sys.exit(0)
```

**DDD Boundary**: This is the ONLY place JSON output logic exists

#### TASK-015: Conversation Loading
**Assigned Libraries**: Existing Conversation class
**95% API Must Work**:
```python
data = hook_input()
conv = data.load_conversation()  # Method on HookData
messages = conv.with_errors()  # Full SDK power
```

**Success Criteria**:
- [ ] Method on HookData (not separate function)
- [ ] Returns existing Conversation object (DRY)
- [ ] Lazy loading (doesn't load unless called)
- [ ] Uses transcript_path from hook data

**SOLID Compliance**:
- Uses existing Conversation (DRY)
- Doesn't duplicate parsing logic (Single Responsibility)
- Works with all hook types (Liskov Substitution)

### EPIC-006: File Watching (Synchronous Mode)
**Goal**: Monitor JSONL files with 1 function call, no async complexity
**Principles**:
- **S**ingle Responsibility: Watch → Parse → Callback
- **O**pen/Closed: Extensible via callbacks
- **DDD**: ConversationMonitor is the aggregate root

#### TASK-016: Core Monitor Class
**Assigned Libraries**: watchfiles (sync mode), orjson, pathlib
**Internal API (not exposed to 95% users)**:
```python
class ConversationMonitor:
    """Domain aggregate for monitoring."""
    def __init__(self, filepath: Path): ...
    def watch(self, callback: Callable): ...
    def _parse_incremental(self): ...
```

**Success Criteria**:
- [ ] Uses watchfiles in SYNC mode (no async/await)
- [ ] Incremental parsing (tracks last_position)
- [ ] UUID deduplication (tracks seen_uuids)
- [ ] Handles file rotation (Change.added)
- [ ] NO public methods except watch()

**DDD Boundaries**:
- ConversationMonitor owns the file watching domain
- Conversation owns the parsing domain
- Clear separation of concerns

#### TASK-017: Simple Watch Function (95% API)
**Assigned Libraries**: ConversationMonitor (internal)
**95% API Must Work**:
```python
from claude_parser import watch

def callback(conv, new_messages):
    print(f"Got {len(new_messages)}")

watch("file.jsonl", callback)  # ONE line!
```

**Success Criteria**:
- [ ] Function signature: `watch(filepath, callback)`
- [ ] NO optional parameters in basic function (95/5)
- [ ] Callback receives (Conversation, List[Message])
- [ ] Runs forever until Ctrl+C
- [ ] Handles all errors internally (no exceptions to user)

**Anti-patterns to AVOID**:
```python
# ❌ WRONG - Too many parameters (violates 95/5)
watch(file, callback, interval=1, buffer=1024, async=False)

# ❌ WRONG - Async complexity
async def watch(): ...
await watch()

# ❌ WRONG - Returns complex object (violates 95/5)
monitor = watch(file)
monitor.on('change', callback)
monitor.start()
```

#### TASK-018: Advanced Watch Control (5% API)
**For users who need more control**:
```python
from claude_parser.watch import ConversationMonitor

monitor = ConversationMonitor("file.jsonl")
# Custom control for 5% users
monitor.watch(callback)
```

**Success Criteria**:
- [ ] Only exposed via submodule import
- [ ] Provides access to internals (last_position, seen_uuids)
- [ ] Still synchronous (no async)

#### TASK-019: Event Signals (Optional)
**Assigned Libraries**: blinker
**For users who want events**:
```python
from claude_parser.watch import signals

signals.new_messages.connect(handler)
signals.file_rotated.connect(handler)
```

**Success Criteria**:
- [ ] Optional feature (doesn't affect 95% API)
- [ ] Uses blinker's simple signal pattern
- [ ] No custom event system (violates DRY)

### EPIC-007: Testing & Documentation

#### TASK-020: Hook Helper Tests
**Test Coverage Requirements**:
```python
# tests/test_hooks.py
def test_all_8_hook_types():
    """Single HookData works for all types."""
    
def test_exit_codes():
    """Exit functions produce correct codes."""
    
def test_json_output():
    """JSON output matches official spec."""
    
def test_conversation_loading():
    """Can load conversation from hook data."""
```

**Success Criteria**:
- [ ] 100% coverage of hook helpers
- [ ] Tests for all 8 hook types
- [ ] Tests for malformed input
- [ ] Performance: < 10ms to parse hook input

#### TASK-021: File Watching Tests
```python
# tests/test_watch.py
def test_incremental_parsing():
    """Only new lines are parsed."""
    
def test_deduplication():
    """UUID deduplication works."""
    
def test_file_rotation():
    """Handles file recreation."""
    
def test_memory_constant():
    """Memory doesn't grow with file size."""
```

**Success Criteria**:
- [ ] Tests with real file operations
- [ ] Tests for race conditions
- [ ] Memory profiling included
- [ ] Performance: < 100ms to detect changes

#### TASK-022: Integration Tests
```python
# tests/test_integration_phase2.py
def test_hook_with_real_claude_format():
    """Test with actual Claude hook JSON."""
    
def test_watch_with_real_jsonl():
    """Test with actual Claude transcript."""
```

**Success Criteria**:
- [ ] Uses real Claude Code JSON formats
- [ ] Tests error scenarios
- [ ] Tests large files (100MB+)

## Acceptance Criteria for Phase 2

### The 95/5 Test
**These MUST work with zero configuration:**

```python
# Hook Helper (3 lines)
from claude_parser.hooks import hook_input, exit_success, exit_block
data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()

# File Watching (3 lines)
from claude_parser import watch
def on_new(conv, msgs): print(f"Got {len(msgs)}")
watch("file.jsonl", on_new)
```

### The DRY Test
Run this grep, should return ZERO:
```bash
# No duplicate parsing logic
grep -r "json.loads" --include="*.py" claude_parser/hooks/
grep -r "sys.stdin.read" --include="*.py" --exclude="hook_input" claude_parser/

# No duplicate models
grep -r "class.*ToolUse.*Data" --include="*.py" claude_parser/
grep -r "class.*PostToolUse.*Data" --include="*.py" claude_parser/
```

### The SOLID Test
```python
# S - Single Responsibility
assert len(hook_input.__doc__.split('\n')) <= 3  # One purpose

# O - Open/Closed  
assert HookData.__subclasses__() == []  # No subclassing needed

# L - Liskov Substitution
for hook_type in ALL_8_TYPES:
    data = hook_input()  # Same interface works

# I - Interface Segregation
assert len(mandatory_imports) <= 3  # Minimal surface

# D - Dependency Inversion
assert 'watchfiles' not in core_imports  # Optional dependency
```

### The Performance Test
```python
# Hook parsing < 10ms
start = time.time()
data = hook_input()
assert (time.time() - start) < 0.01

# File watching < 100ms detection
# Memory usage constant (not growing with file)
```

## Priority Order

1. **TASK-012**: Hook Input Parser (enables hook-v2 project)
2. **TASK-013**: Exit Helpers (completes hook MVP)
3. **TASK-020**: Hook Tests (ensures quality)
4. **TASK-016**: Monitor Class (enables memory project)
5. **TASK-017**: Watch Function (completes watch MVP)
6. **TASK-021**: Watch Tests (ensures quality)
7. Everything else

## Definition of Done

- [ ] Follows SOLID/DRY/DDD principles
- [ ] 95% API works in ≤ 3 lines
- [ ] Zero unnecessary dependencies
- [ ] Tests written FIRST (TDD)
- [ ] Performance benchmarks pass
- [ ] Documentation shows 95% and 5% usage
- [ ] No asyncio complexity exposed to users

## Session Handoff

When implementing:
1. Read this backlog item completely
2. Check SPECIFICATION.md for library rules
3. Write the test FIRST
4. Implement the SIMPLEST solution
5. If it takes > 3 lines for 95% case, STOP and rethink
6. Run verification commands
7. Update status in this file