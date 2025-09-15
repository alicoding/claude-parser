# 🎯 CG Implementation Roadmap
@NEURAL_TIMESTAMP: 2025-01-14T16:00:00Z
@CG_ROADMAP @TOKEN_EFFICIENT_DEVELOPMENT @FRAMEWORK_FIRST

## Vision: Every API Call = Automatic Git Commit
**Better than git because EVERY operation is tracked!**
- File deleted → `cg checkout file.py` → 0 tokens (like git checkout)
- Need previous state → `cg reset --hard UUID` → 0 tokens (like git reset)
- Undo last change → `cg revert HEAD` → 0 tokens (like git revert)
- Each Claude message = automatic commit with UUID

## 🏗️ Implementation Plan with 100% Framework Delegation

### Phase 1: DuckDB Integration [@DUCKDB_JSONL]
**File**: `storage/jsonl_engine.py` (<80 LOC)
```python
import duckdb

def query_jsonl(jsonl_path: str, sql: str):
    """100% DuckDB delegation - zero custom logic"""
    return duckdb.sql(f"SELECT * FROM '{jsonl_path}' {sql}").df()

# THAT'S IT! Everything else REUSES existing functions!
```

### Phase 2: REUSE Existing Navigation [@DRY_FIRST]
**Already exists in** `navigation/timeline.py`:
- ✅ `find_message_by_uuid()` - Navigate to any UUID
- ✅ `get_message_sequence()` - Get range of messages
- ✅ `get_timeline_summary()` - Overview of session

**Already exists in** `navigation/checkpoint.py`:
- ✅ `find_current_checkpoint()` - Last file operation
- ✅ `_find_triggering_user_message()` - What caused change

**NO NEW FUNCTIONS NEEDED!**

### Phase 3: REUSE Existing Operations [@UTIL_FIRST]
**Already exists in** `operations/core.py`:
- ✅ `restore_file_content()` - Write file to disk
- ✅ `generate_file_diff()` - Create unified diff
- ✅ `compare_files()` - Compare two files
- ✅ `backup_file()` - Create backup

**COMPOSE, don't create!**

### Phase 4: CLI Commands [@CLI_CG_COMPLETE]
**File**: `cli/cg.py` (extend existing)

#### `cg checkout [target]`
```python
@app.command()
def checkout(target: Optional[str] = None):
    """Navigate to checkpoint or restore file (0 tokens!)"""
    session = load_latest_session()
    jsonl_path = get_jsonl_path(session)

    if Path(target).exists():  # Single file
        content = get_file_at_uuid(jsonl_path, find_current_checkpoint(), target)
        restore_file_content(target, content)  # operations/core.py
    elif target:  # UUID
        files = get_files_at_checkpoint(session, target)
        for file_path, content in files:
            restore_file_content(file_path, content)
    else:  # List checkpoints
        show_checkpoints(session)
```

#### `cg restore <file>`
```python
@app.command()
def restore(file_path: str, checkpoint: Optional[str] = None):
    """Restore single file from JSONL history"""
    # Pure delegation to get_file_at_uuid + restore_file_content
```

#### `cg diff [uuid1] [uuid2]`
```python
@app.command()
def diff(uuid1: Optional[str] = None, uuid2: Optional[str] = None):
    """Show changes between checkpoints"""
    # Use operations/generate_file_diff with JSONL content
```

#### `cg blame <file>`
```python
@app.command()
def blame(file_path: str):
    """Show tool attribution per line"""
    history = get_file_history(session, file_path)
    # Format with Rich tables
```

#### `cg reset [--hard] [--soft] <uuid>`
```python
@app.command()
def reset(uuid: str, hard: bool = False, soft: bool = False):
    """Reset to checkpoint (like git reset)"""
    # --hard: restore files to disk
    # --soft: just move pointer
    # Mimics git reset exactly
```

#### `cg revert <uuid>`
```python
@app.command()
def revert(uuid: str):
    """Create opposite of a change (like git revert)"""
    # Takes a tool operation and undoes it
    # Keeps history intact
```

#### `cg stash` / `cg stash pop`
```python
@app.command()
def stash():
    """Save current changes temporarily"""
    # Since every API call is tracked, we can stash/unstash
```

### Phase 5: Token Tracking [@TOKEN_SAVINGS]
**File**: `tokens/savings.py`
```python
def calculate_savings(original_tokens: int, cg_tokens: int = 0):
    """Show token savings from using cg"""
    # original_tokens from message.usage
    # cg uses 0 tokens!
```

## 🔧 Framework Stack (100% Delegation)

| Component | Framework | Pattern |
|-----------|-----------|---------|
| JSONL Query | DuckDB | SQL on JSONL files |
| Navigation | more-itertools | first(), take(), dropwhile() |
| File Ops | pathlib | read_bytes(), write_bytes() |
| Diff | difflib | unified_diff() |
| CLI | Typer | @app.command() |
| Display | Rich | Table, Console |
| Schema | genson | SchemaBuilder (for discovery) |

## 📊 Testing Strategy

### Black Box with Real Data
```python
def test_checkout_with_actual_conversation():
    """Use THIS conversation as test data"""
    # This conversation created memory_map.md
    result = run(['cg', 'checkout', 'memory_map.md'])
    assert Path('memory_map.md').read_text() == original_content
```

### Integration Tests
```python
def test_anti_pattern_recovery():
    """Test 0-token recovery from violations"""
    # Create file >80 LOC (violation)
    # Use cg revert --before-violation
    # Verify file restored to <80 LOC
```

## 🎯 Success Metrics

1. **Token Savings**: 5000 tokens per undo operation
2. **Speed**: Instant restoration (no Claude API calls)
3. **Coverage**: All Write/Edit/MultiEdit operations reversible
4. **UX**: Git-like commands familiar to developers

## 🚀 Next Session Pickup Points

### @CG_PHASE_1
→ `storage/jsonl_engine.py` - DuckDB integration

### @CG_PHASE_2
→ `navigation/timeline.py` - Enhance with file history

### @CG_PHASE_3
→ `navigation/checkpoint.py` - Multi-file restoration

### @CG_PHASE_4
→ `cli/cg.py` - Implement all commands

### @CG_PHASE_5
→ `tokens/savings.py` - Track savings

## 🔑 Key Insights

1. **JSONL has EVERYTHING**: toolUseResult.content has full file contents
2. **DuckDB reads JSONL natively**: No parsing needed
3. **Every operation reversible**: UUID + timestamp = time travel
4. **0 tokens to undo**: Compare to 5000+ for Claude to rewrite
5. **Anti-pattern prevention**: Detect and revert automatically

## Neural Navigation Tags

- `@CG_ROADMAP` → This file
- `@DUCKDB_JSONL` → storage/jsonl_engine.py implementation
- `@NAV_TIMELINE_POWER` → navigation/timeline.py enhancements
- `@NAV_CHECKPOINT_POWER` → navigation/checkpoint.py restoration
- `@CLI_CG_COMPLETE` → cli/cg.py full implementation
- `@TOKEN_SAVINGS` → tokens/savings.py metrics

This is the complete blueprint for Token-Efficient Development!