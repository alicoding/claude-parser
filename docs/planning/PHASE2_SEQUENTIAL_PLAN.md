# Phase 2: Sequential TDD Implementation Plan

## 🎯 Mission Statement
Deliver Phase 2 with **ZERO technical debt**, **ZERO bugs**, following **SOLID/DRY/DDD/TDD** and **95/5** principles so strictly that this becomes the reference implementation for "doing it right."

## 📏 Success Metrics
- **Test Coverage**: 100% (not negotiable)
- **Code for 95% case**: ≤ 3 lines
- **Technical Debt**: 0 (measured by TODO/FIXME/HACK comments)
- **Cyclomatic Complexity**: < 5 per function
- **Dependencies**: Minimal, explicit, optional
- **Time to first value**: < 5 minutes for new users

---

## 🔄 Sequential Implementation Order (TDD)

### Phase 2A: Hook Helpers (Zero New Dependencies)

#### Step 1: Test Infrastructure
**Why First**: Can't do TDD without test infrastructure
**Files**:
```
tests/
├── test_phase2/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures
│   ├── test_hook_models.py  # Step 2 tests
│   ├── test_hook_input.py   # Step 3 tests
│   ├── test_hook_exits.py   # Step 4 tests
│   └── test_hook_integration.py  # Step 6 tests
```

**Todo**:
```python
# tests/test_phase2/conftest.py
import pytest
import json
import sys
from io import StringIO

@pytest.fixture
def mock_stdin():
    """Mock stdin for testing hook input."""
    def _mock(data: dict):
        old_stdin = sys.stdin
        sys.stdin = StringIO(json.dumps(data))
        yield
        sys.stdin = old_stdin
    return _mock

@pytest.fixture
def capture_exit():
    """Capture sys.exit calls."""
    # Implementation here
```

**Verification**: `pytest tests/test_phase2/conftest.py` loads without error

---

#### Step 2: Hook Data Model (TDD)
**Why Next**: Core domain model, everything depends on this
**Test First** (`tests/test_phase2/test_hook_models.py`):
```python
def test_hook_data_accepts_all_8_types():
    """Single model handles all hook types (DRY)."""
    hook_types = [
        "PreToolUse", "PostToolUse", "Notification",
        "UserPromptSubmit", "Stop", "SubagentStop", 
        "PreCompact", "SessionStart"
    ]
    
    for hook_type in hook_types:
        data = HookData(
            session_id="test",
            transcript_path="/path/to/transcript.jsonl",
            cwd="/current/dir",
            hook_event_name=hook_type
        )
        assert data.hook_event_name == hook_type
        assert data.hook_type == hook_type  # Convenience property

def test_hook_data_optional_fields():
    """Optional fields work correctly."""
    # Minimal required fields
    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse"
    )
    assert data.tool_name is None
    assert data.tool_input is None
    
    # With optional fields
    data = HookData(
        session_id="test",
        transcript_path="/path/to/transcript.jsonl",
        cwd="/current/dir",
        hook_event_name="PreToolUse",
        tool_name="Write",
        tool_input={"file_path": "/test.txt"}
    )
    assert data.tool_name == "Write"
    assert data.tool_input["file_path"] == "/test.txt"

def test_hook_data_immutable():
    """Models are immutable (frozen=True)."""
    data = HookData(...)
    with pytest.raises(AttributeError):
        data.session_id = "changed"
```

**Implementation** (`claude_parser/hooks/models.py`):
```python
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

HookEventType = Literal[
    "PreToolUse", "PostToolUse", "Notification",
    "UserPromptSubmit", "Stop", "SubagentStop", 
    "PreCompact", "SessionStart"
]

class HookData(BaseModel):
    """Universal hook data model (DRY principle)."""
    class Config:
        frozen = True  # Immutable
        extra = "allow"  # Forward compatibility
    
    # Required fields (all hooks have these)
    session_id: str
    transcript_path: str
    cwd: str
    hook_event_name: HookEventType
    
    # Optional fields (hook-specific)
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_response: Optional[Dict[str, Any]] = None
    prompt: Optional[str] = None
    message: Optional[str] = None
    stop_hook_active: Optional[bool] = None
    trigger: Optional[str] = None
    custom_instructions: Optional[str] = None
    source: Optional[str] = None
    
    @property
    def hook_type(self) -> str:
        """Convenience alias for 95% users."""
        return self.hook_event_name
    
    def load_conversation(self):
        """Load conversation using Phase 1 parser."""
        from claude_parser import load
        return load(self.transcript_path)
```

**Verification**: `pytest tests/test_phase2/test_hook_models.py -v` (100% pass)

---

#### Step 3: Hook Input Function (TDD)
**Why Next**: Core 95% API function
**Test First** (`tests/test_phase2/test_hook_input.py`):
```python
def test_hook_input_parses_stdin(mock_stdin):
    """hook_input() parses JSON from stdin."""
    test_data = {
        "session_id": "abc123",
        "transcript_path": "/path/to/transcript.jsonl",
        "cwd": "/current/dir",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write"
    }
    
    with mock_stdin(test_data):
        data = hook_input()
    
    assert data.session_id == "abc123"
    assert data.tool_name == "Write"

def test_hook_input_handles_invalid_json(mock_stdin, capsys):
    """Graceful error on invalid JSON."""
    sys.stdin = StringIO("not json")
    
    with pytest.raises(SystemExit) as exc:
        hook_input()
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.err

def test_hook_input_handles_missing_fields(mock_stdin, capsys):
    """Graceful error on missing required fields."""
    with mock_stdin({"session_id": "test"}):  # Missing required fields
        with pytest.raises(SystemExit) as exc:
            hook_input()
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Missing required" in captured.err
```

**Implementation** (`claude_parser/hooks/__init__.py`):
```python
import sys
import orjson
from typing import NoReturn
from pydantic import ValidationError
from .models import HookData

def hook_input() -> HookData:
    """
    Parse hook input from stdin.
    
    95% Use Case:
        data = hook_input()  # That's it!
    
    Returns:
        HookData with all fields populated
        
    Exits:
        1: On any error (with stderr message)
    """
    try:
        raw = sys.stdin.read()
        data = orjson.loads(raw)
        return HookData(**data)
    except orjson.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: Missing required fields: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

**Verification**: `pytest tests/test_phase2/test_hook_input.py -v` (100% pass)

---

#### Step 4: Exit Helpers (TDD)
**Why Next**: Complete the 95% API
**Test First** (`tests/test_phase2/test_hook_exits.py`):
```python
def test_exit_success_with_no_message(capsys):
    """exit_success() exits 0 with optional stdout."""
    with pytest.raises(SystemExit) as exc:
        exit_success()
    
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""

def test_exit_success_with_message(capsys):
    """exit_success() can include stdout message."""
    with pytest.raises(SystemExit) as exc:
        exit_success("All good")
    
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert captured.out == "All good\n"
    assert captured.err == ""

def test_exit_block_requires_reason(capsys):
    """exit_block() exits 2 with stderr reason."""
    with pytest.raises(SystemExit) as exc:
        exit_block("Security violation")
    
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "Security violation\n"

def test_exit_error_non_blocking(capsys):
    """exit_error() exits 1 with stderr."""
    with pytest.raises(SystemExit) as exc:
        exit_error("Warning message")
    
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.err == "Warning message\n"
```

**Implementation** (`claude_parser/hooks/__init__.py` - add to existing):
```python
def exit_success(message: str = "") -> NoReturn:
    """
    Exit with success (code 0).
    
    Args:
        message: Optional stdout message (shown in transcript mode)
    """
    if message:
        print(message)
    sys.exit(0)

def exit_block(reason: str) -> NoReturn:
    """
    Exit with blocking error (code 2).
    
    Args:
        reason: Required reason shown to Claude
    """
    print(reason, file=sys.stderr)
    sys.exit(2)

def exit_error(message: str) -> NoReturn:
    """
    Exit with non-blocking error (code 1).
    
    Args:
        message: Error message shown to user
    """
    print(message, file=sys.stderr)
    sys.exit(1)
```

**Verification**: `pytest tests/test_phase2/test_hook_exits.py -v` (100% pass)

---

#### Step 5: Advanced Features (5% API) - TDD
**Why Next**: Complete hook helpers before moving to file watching
**Test First** (`tests/test_phase2/test_hook_advanced.py`):
```python
def test_json_output_pretooluse_format(capsys):
    """JSON output for PreToolUse uses hookSpecificOutput."""
    with pytest.raises(SystemExit) as exc:
        json_output(
            hook_type="PreToolUse",
            decision="deny",
            reason="Security"
        )
    
    assert exc.value.code == 0
    output = json.loads(capsys.readouterr().out)
    assert "hookSpecificOutput" in output
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"

def test_json_output_other_hooks(capsys):
    """JSON output for other hooks uses simple format."""
    with pytest.raises(SystemExit) as exc:
        json_output(
            hook_type="PostToolUse",
            decision="block",
            reason="Failed"
        )
    
    output = json.loads(capsys.readouterr().out)
    assert output["decision"] == "block"
    assert output["reason"] == "Failed"

def test_advanced_methods():
    """Advanced convenience methods generate correct JSON."""
    # Test each advanced method
    pass
```

**Implementation** (`claude_parser/hooks/advanced.py`):
```python
"""
Advanced hook features for 5% use cases.
Not needed for basic hooks.
"""

def json_output(hook_type: str = None, decision: str = None, 
                reason: str = None, **kwargs) -> NoReturn:
    """
    Output JSON response for advanced control.
    
    5% Use Case - when exit codes aren't enough.
    """
    # Implementation matching Claude's expectations
    pass

# Convenience methods (optional)
def allow(reason: str = "") -> NoReturn:
    """PreToolUse: Allow tool execution."""
    pass

def deny(reason: str) -> NoReturn:
    """PreToolUse: Deny tool execution."""
    pass

def ask() -> NoReturn:
    """PreToolUse: Ask user for permission."""
    pass

def add_context(context: str) -> NoReturn:
    """UserPromptSubmit: Add context."""
    pass
```

**Verification**: `pytest tests/test_phase2/test_hook_advanced.py -v` (100% pass)

---

#### Step 6: Integration Tests
**Why Last**: Verify everything works together
**Test** (`tests/test_phase2/test_hook_integration.py`):
```python
def test_complete_hook_flow():
    """End-to-end test of hook functionality."""
    # Create temp transcript file
    transcript = create_test_transcript()
    
    # Mock stdin with real Claude format
    stdin_data = {
        "session_id": "abc123",
        "transcript_path": str(transcript),
        "cwd": "/test",
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/etc/passwd"}
    }
    
    # Test complete flow
    with mock_stdin(stdin_data):
        data = hook_input()
        assert data.tool_name == "Write"
        
        # Load conversation
        conv = data.load_conversation()
        assert len(conv) > 0
        
        # Make decision
        if "passwd" in data.tool_input.get("file_path", ""):
            with pytest.raises(SystemExit) as exc:
                exit_block("Protected file")
            assert exc.value.code == 2

def test_performance():
    """Hook processing < 10ms."""
    import time
    start = time.time()
    
    with mock_stdin(valid_data):
        data = hook_input()
    
    elapsed = time.time() - start
    assert elapsed < 0.01  # 10ms
```

**Verification**: `pytest tests/test_phase2/test_hook_integration.py -v` (100% pass)

---

### Phase 2B: File Watching (Optional Install)

#### Step 7: Watch Models (TDD)
**Test First** (`tests/test_phase2/test_watch_models.py`):
```python
def test_conversation_monitor_init():
    """Monitor initializes with file state."""
    monitor = ConversationMonitor("test.jsonl")
    assert monitor.filepath == Path("test.jsonl")
    assert monitor.last_position == 0
    assert len(monitor.seen_uuids) == 0
```

**Implementation** (`claude_parser/watch/monitor.py`):
```python
# Implementation following TDD
```

#### Step 8: Incremental Parsing (TDD)
**Test First**: Only new lines parsed, not entire file
**Implementation**: Track position, read incrementally

#### Step 9: Simple Watch Function (95% API)
**Test First**: One-line watching works
**Implementation**: Wrap monitor complexity

#### Step 10: Integration & Performance
**Test First**: Memory stays constant, < 100ms detection
**Implementation**: Verify all requirements met

---

## 🎯 Delivery Checklist

### Before Starting Each Step
- [ ] Read the test requirements
- [ ] Write the test FIRST (must fail)
- [ ] Write MINIMAL code to pass
- [ ] Refactor if needed (tests still pass)
- [ ] Check SOLID compliance
- [ ] Check DRY compliance
- [ ] Check 95/5 compliance
- [ ] Run ALL tests (not just new ones)

### After Each Step
- [ ] Test coverage = 100%
- [ ] No TODO/FIXME/HACK comments
- [ ] Documentation complete
- [ ] Complexity < 5
- [ ] 95% API ≤ 3 lines

### Before Release
- [ ] All tests pass
- [ ] Performance benchmarks pass
- [ ] Memory profiling complete
- [ ] Security review done
- [ ] Documentation complete
- [ ] Examples provided
- [ ] Migration guide written

---

## 📊 Zero Technical Debt Metrics

```python
# Run these checks after EVERY commit
def check_technical_debt():
    """Zero tolerance for technical debt."""
    
    # No TODO/FIXME/HACK
    assert grep("TODO|FIXME|HACK", "**/*.py") == []
    
    # No disabled tests
    assert grep("@pytest.mark.skip", "tests/") == []
    
    # No commented code
    assert grep("^\\s*#.*\\(\\)|\\{|\\[", "**/*.py") == []
    
    # 100% test coverage
    assert coverage_report() == 100.0
    
    # No type: ignore
    assert grep("type: ignore", "**/*.py") == []
    
    # Complexity check
    assert max_complexity() < 5
    
    print("✅ ZERO TECHNICAL DEBT")
```

---

## 🚀 Why This Order?

1. **Test Infrastructure First**: Can't do TDD without it
2. **Models Before Logic**: Domain models are the foundation
3. **Core Before Advanced**: 95% API before 5% features
4. **Unit Before Integration**: Build up from small to large
5. **Hooks Before Watching**: Simpler feature first
6. **Each Step Enables Next**: True sequential dependency

---

## ✅ Success Criteria

### For Your Projects
- **hook-v2**: 3 lines to replace 15+ lines of cchooks
- **memory**: 1 line to replace 513 lines of monitoring
- **Both**: Zero bugs, zero technical debt

### For Open Source
- Reference implementation of SOLID/DRY/DDD/TDD
- Example of true 95/5 API design
- Proof that "doing it right" is achievable

---

## 📝 Final Notes

This plan is **sequential**, **testable**, and **deliverable**. Each step:
1. Has clear tests written FIRST
2. Builds on previous steps
3. Maintains zero technical debt
4. Follows all principles strictly
5. Delivers immediate value

Ready to execute with **zero compromises** on quality.