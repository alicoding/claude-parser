# Fix All Skipped Tests - Zero Skip Policy

**Issue**: 15 tests are being skipped, hiding potential problems
**Policy**: NO SKIPPED TESTS - Either implement or mark as xfail with reason

---

## Current Skipped Tests Analysis

### 1. test_navigation.py (1 skipped)
```python
# Line 127: Session boundaries not implemented yet
pytest.skip("Session boundaries not implemented yet")
```
**FIX**: Implement `get_session_boundaries()` method

### 2. test_phase3/test_watch_api.py (14 skipped)
All marked as "Implementation pending" for watch functionality:
- test_message_type_filtering
- test_file_rotation_handling
- test_error_callback
- test_watch_with_invalid_path
- test_watch_with_empty_file
- test_watch_handles_parse_errors
- test_callback_exception_handling
- test_multiple_file_changes
- test_watch_timeout
- test_watch_can_be_stopped
- test_watch_memory_efficiency
- test_watch_cpu_efficiency
- test_watch_responsiveness
- test_watch_handles_rapid_changes

**FIX**: Either:
1. Implement the watch functionality (if needed)
2. Mark as `@pytest.mark.xfail(reason="Watch feature not yet implemented")`
3. Remove if feature not planned

---

## Implementation Plan

### Option 1: Fix Session Boundaries (Quick Win)

```python
# In claude_parser/domain/entities/conversation.py
def get_session_boundaries(self) -> List[int]:
    """Get indices where session changes occur."""
    boundaries = []
    current_session = None

    for i, msg in enumerate(self._messages):
        if hasattr(msg, 'session_id') and msg.session_id:
            if current_session is None:
                boundaries.append(i)  # First session starts
                current_session = msg.session_id
            elif msg.session_id != current_session:
                boundaries.append(i)  # New session starts
                current_session = msg.session_id

    return boundaries
```

### Option 2: Convert Skips to XFail

Replace all `pytest.skip()` with:
```python
@pytest.mark.xfail(reason="Feature not implemented - tracked in issue #XXX")
```

This way:
- Tests still run (find crashes/errors)
- Clear documentation of what's missing
- Can't accidentally skip important tests
- Shows up differently in reports

### Option 3: Remove Unused Tests

If watch functionality isn't planned, remove the tests entirely rather than skip.

---

## Immediate Actions Required

1. **Fix test_navigation.py session boundaries** - Easy implementation
2. **Decision on watch API** - Keep and implement, or remove?
3. **Update conftest.py fixtures** - Ensure no skips for missing files
4. **Review all conditional skips** - Replace file existence checks with fixtures

---

## Code Changes Needed

### 1. Fix Session Boundaries
```python
# claude_parser/domain/entities/conversation.py
class Conversation:
    def get_session_boundaries(self) -> List[int]:
        """Get indices where session ID changes."""
        if not self._messages:
            return []

        boundaries = [0]  # First message is always a boundary
        current_session = getattr(self._messages[0], 'session_id', None)

        for i, msg in enumerate(self._messages[1:], 1):
            msg_session = getattr(msg, 'session_id', None)
            if msg_session != current_session:
                boundaries.append(i)
                current_session = msg_session

        return boundaries
```

### 2. Fix Fixture-Based Skips
```python
# In conftest.py - Never skip, provide fallback
@pytest.fixture
def sample_jsonl():
    """Always provide a file, never skip."""
    files = [
        Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/4762e53b-7ca8-4464-9eac-d1816c343c50.jsonl"),
        Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl"),
        Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/840f9326-6f99-46d9-88dc-f32fb4754d36.jsonl"),
    ]

    for f in files:
        if f.exists():
            return f

    # Create minimal valid JSONL if no files exist
    # This ensures tests ALWAYS run
    temp_file = Path("/tmp/test_claude.jsonl")
    temp_file.write_text('''{"type":"summary","summary":"Test","leafUuid":"test-uuid"}''')
    return temp_file
```

### 3. Replace Skip with XFail
```python
# Instead of:
def test_something():
    pytest.skip("Not implemented")

# Use:
@pytest.mark.xfail(reason="Not implemented - see issue #123")
def test_something():
    # Test code that will fail
    assert False, "This feature needs implementation"
```

---

## Benefits of Zero-Skip Policy

1. **No Hidden Problems**: Skipped tests hide crashes and errors
2. **Clear Status**: XFail shows what's broken vs what's missing
3. **Better Planning**: Forces decision on each test
4. **Prevents Rot**: Can't ignore tests indefinitely
5. **CI/CD Clarity**: Build knows exactly what's expected to work

---

## Test Categories After Fix

- **PASS**: Working as expected ✅
- **XFAIL**: Known to fail, documented reason ⚠️
- **FAIL**: Unexpected failure, needs fix ❌
- **ERROR**: Test has problems ❌
- ~~**SKIP**: Not allowed ~~

No more hidden issues!
