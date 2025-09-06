# Critical Gaps Action Plan - Claude Parser

**Created**: 2025-08-25
**Status**: ACTION REQUIRED
**Test Health**: 228 passing, 37 failing, 19 errors

---

## 🔴 P0 - IMMEDIATE BLOCKERS (Fix Today)

### 1. Create Missing `sample_jsonl` Fixture Using Real Data
**Impact**: 48+ tests failing
**Location**: `tests/conftest.py`
**Action**:
```python
@pytest.fixture
def sample_jsonl():
    """Use real production JSONL data for all tests."""
    # Use the smallest real file for speed
    real_file = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/4762e53b-7ca8-4464-9eac-d1816c343c50.jsonl")
    if not real_file.exists():
        pytest.skip(f"Real production data not found: {real_file}")
    return real_file
```
**Validation**: `pytest tests/test_conversation.py -v` should pass

### 2. Fix Test Import Dependencies
**Impact**: 19 test errors
**Issues**:
- Missing imports for SessionAnalyzer
- Incorrect module paths after refactoring
**Action**:
- Update all test imports to match new structure
- Add `__init__.py` files where missing
**Validation**: `pytest tests/ --collect-only` should have 0 errors

---

## 🔴 P1 - CRITICAL DATA INTEGRITY (This Week)

### 3. Add Domain Invariant Validation
**Gap**: No validation for invalid states
**Location**: `claude_parser/domain/entities/conversation.py`
**Required Validations**:
```python
def validate_invariants(self):
    """Enforce domain rules that must always be true."""
    # 1. No duplicate UUIDs
    uuids = [msg.uuid for msg in self._messages if hasattr(msg, 'uuid')]
    if len(uuids) != len(set(uuids)):
        raise DomainInvariantViolation("Duplicate message UUIDs detected")

    # 2. Chronological timestamp order
    timestamps = [msg.timestamp for msg in self._messages if msg.timestamp]
    if timestamps != sorted(timestamps):
        raise DomainInvariantViolation("Messages not in chronological order")

    # 3. Tool use/result pairing
    # Every tool_use should have matching tool_result
    tool_uses = {}
    for msg in self._messages:
        if hasattr(msg, 'content_blocks'):
            for block in msg.content_blocks:
                if block.type == 'tool_use':
                    tool_uses[block.id] = True
                elif block.type == 'tool_result':
                    tool_uses.pop(block.tool_use_id, None)
    if tool_uses:
        raise DomainInvariantViolation(f"Unmatched tool uses: {list(tool_uses.keys())}")
```
**Test**: Create test with duplicate UUIDs, should raise exception

### 4. Fix Session Boundary Detection
**Gap**: Only looks at first session_id, ignores boundaries
**Location**: `claude_parser/domain/services/session_analyzer.py`
**Fix**:
```python
def find_session_boundaries(self, conversation) -> List[int]:
    """Find all session boundary indices."""
    boundaries = [0]  # Start of first session
    current_session = None

    for i, msg in enumerate(conversation.messages):
        if hasattr(msg, 'session_id') and msg.session_id:
            if current_session and msg.session_id != current_session:
                boundaries.append(i)  # New session starts here
            current_session = msg.session_id

    return boundaries
```
**Test**: Multi-session conversation should split correctly

### 5. Consolidate Token Calculation (DRY Violation)
**Gap**: Duplicated in 3 places
**Action**: Use only `TokenService` for all calculations
**Locations to fix**:
- Remove `TokenAnalyzer._calculate_cost()` → use `TokenService`
- Remove `ConversationAnalytics._add_token_estimates()` → use `TokenService`
- Update all references to use centralized service
**Validation**: All cost calculations should match exactly

---

## 🟡 P2 - PERFORMANCE & RELIABILITY (Next Sprint)

### 6. Fix NavigationService Architecture
**Gap**: Rebuilds indices on every instantiation (O(N))
**Current Problem**:
```python
def __init__(self, conversation):
    self.conversation = conversation
    self._build_indices()  # ← Expensive, runs every time!
```
**Solution**: Lazy loading with caching
```python
class NavigationService:
    def __init__(self, conversation):
        self.conversation = conversation
        self._indices = None  # Lazy load
        self._cache_valid = False

    @property
    def indices(self):
        if not self._cache_valid:
            self._build_indices()
            self._cache_valid = True
        return self._indices
```
**Test**: Large conversation (1000+ messages) performance test

### 7. Add Context Window Management
**CLARIFICATION**: Auto-compact at 90% (180K of 200K tokens)

**What is Auto-Compact?**
When a Claude conversation approaches the 200K token context limit, Claude automatically creates a "compact summary" to free up space. This happens at ~90% capacity (180K tokens).

**Implementation Needed**:
```python
class ContextWindowManager:
    CONTEXT_LIMIT = 200_000  # Claude 3.5 Sonnet limit
    COMPACT_THRESHOLD = 0.9  # Trigger at 90%

    def should_compact(self, total_tokens: int) -> bool:
        """Check if we should trigger auto-compact."""
        return total_tokens >= (self.CONTEXT_LIMIT * self.COMPACT_THRESHOLD)

    def calculate_tokens_until_compact(self, total_tokens: int) -> int:
        """Calculate tokens remaining until auto-compact triggers."""
        compact_point = int(self.CONTEXT_LIMIT * self.COMPACT_THRESHOLD)
        return max(0, compact_point - total_tokens)

    def format_warning(self, total_tokens: int) -> str:
        """Format user-friendly warning about approaching limit."""
        percent = (total_tokens / self.CONTEXT_LIMIT) * 100
        tokens_left = self.calculate_tokens_until_compact(total_tokens)

        if percent >= 90:
            return f"🔴 CRITICAL: {percent:.1f}% used - Auto-compact imminent!"
        elif percent >= 75:
            return f"🟠 WARNING: {percent:.1f}% used - {tokens_left:,} tokens until compact"
        else:
            return f"🟢 OK: {percent:.1f}% used - {tokens_left:,} tokens until compact"
```
**Test**: Verify triggers at exactly 180K tokens

### 8. Fix File Watching Race Condition
**Gap**: File could change between stat() and read()
**Location**: `claude_parser/infrastructure/watch.py`
**Fix**: Use file locking or atomic operations
```python
import fcntl

def get_new_lines_safe(self) -> List[str]:
    """Read new lines with file locking to prevent race conditions."""
    with open(self.file_path, 'r', encoding='utf-8') as f:
        # Acquire shared lock for reading
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)
        try:
            f.seek(self.last_position)
            new_lines = f.readlines()
            self.last_position = f.tell()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return new_lines
```
**Test**: Concurrent read/write stress test

### 9. Fix Tool Message Extraction
**Gap**: `tool_uses` returns empty for production data
**Real Pattern**: Tools are in content blocks
```python
@property
def tool_uses(self):
    """Extract tool uses from content blocks in messages."""
    tools = []
    for msg in self._messages:
        # Check nested message structure (real production data)
        if hasattr(msg, 'message') and isinstance(msg.message, dict):
            content = msg.message.get('content', [])
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get('type') in ['tool_use', 'tool_result']:
                            tools.append(block)
    return tools
```
**Test**: Load real production data, verify tool extraction

### 10. Add Error Recovery Access
**Gap**: Can't debug parsing failures - raw JSON discarded
**Solution**: Store raw JSON for failed messages
```python
class MessageRepository:
    def __init__(self):
        self.failed_raw_messages = []  # Store for debugging

    def load_messages(self, filepath):
        # ... existing code ...
        if parse_error:
            self.failed_raw_messages.append({
                'line': line_num,
                'raw_json': raw_line,
                'error': str(error)
            })
```
**Test**: Intentionally corrupt JSONL, verify raw data preserved

---

## 🟢 P3 - CODE QUALITY (Within Month)

### 11. Replace Primitive Obsession with Value Objects
**Locations**:
```python
# Create value objects
class MessageId:
    def __init__(self, value: str):
        if not self._is_valid_uuid(value):
            raise ValueError(f"Invalid UUID: {value}")
        self.value = value

class SessionId:
    def __init__(self, value: str):
        if not value:
            raise ValueError("Session ID cannot be empty")
        self.value = value

class Timestamp:
    def __init__(self, value: str):
        # Validate ISO 8601 format
        self.value = pendulum.parse(value)
```
**Impact**: Type safety, validation at boundaries

### 12. Standardize Functional Programming
**Rule**: Use toolz for all collection operations
**Bad**:
```python
for msg in messages:
    if msg.type == "user":
        users.append(msg)
```
**Good**:
```python
users = pipe(
    messages,
    lambda msgs: filter(lambda m: m.type == "user", msgs),
    list
)
```
**Action**: Refactor all loops to functional style

### 13. Repository Error Abstraction
**Fix**: Map infrastructure errors to domain exceptions
```python
class ConversationService:
    def get_parsing_errors(self) -> List[ParsingError]:
        """Return domain-specific error objects, not raw repo errors."""
        return [
            ParsingError(
                line=err[0],
                message=err[1],
                severity="warning"
            )
            for err in self.repository.errors
        ]
```

### 14. Add Missing Integration Tests
**Required Tests**:
- Tool use/result correlation with real data
- Session boundary detection with multi-session files
- Context overflow at exactly 200K tokens
- Concurrent file watching (multiple readers)
- Performance with 10K+ message conversations
**Location**: `tests/integration/`

### 15. Validate Token Counting Against Temporal-Hooks
**User Concern**: "6% until auto compact"
**Action**:
1. Load actual temporal-hooks JSONL
2. Calculate tokens using our logic
3. Compare with Claude Code UI display
4. Adjust calculation if mismatch found
**Test Case**: Must match Claude Code UI exactly

---

## 📋 Implementation Checklist

### Week 1 (P0 + Critical P1)
- [ ] Create `sample_jsonl` fixture with real data
- [ ] Fix all test imports and dependencies
- [ ] Add domain invariant validation
- [ ] Fix session boundary detection
- [ ] Consolidate token calculation

### Week 2 (P1 + P2)
- [ ] Fix NavigationService architecture
- [ ] Add context window management
- [ ] Fix file watching race condition
- [ ] Fix tool message extraction
- [ ] Add error recovery access

### Week 3-4 (P3)
- [ ] Replace primitives with value objects
- [ ] Standardize functional programming
- [ ] Fix repository abstraction
- [ ] Add integration tests
- [ ] Validate token counting accuracy

---

## 🎯 Success Criteria

1. **Test Suite**: 100% passing (0 failures, 0 errors)
2. **Real Data**: All tests use production JSONL files
3. **Token Accuracy**: Matches Claude Code UI exactly
4. **Performance**: <1s load time for 1000 message conversation
5. **Domain Integrity**: Invalid states impossible to create
6. **Code Quality**: Consistent functional style throughout

---

## 🚨 Risks if Not Fixed

1. **Data Corruption**: Invalid states could persist
2. **Wrong Cost Calculations**: Token counting errors = billing issues
3. **Lost Messages**: Race conditions in file watching
4. **Performance Degradation**: O(N) operations on every access
5. **Context Overflow**: No warning before hitting 200K limit
6. **Debugging Nightmare**: Can't recover from parsing errors

**MUST START WITH**: Creating `sample_jsonl` fixture - this unblocks everything else.
