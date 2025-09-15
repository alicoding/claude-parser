# 🎯 CG Implementation - 100% LNCA Compliant Plan
@NEURAL_TIMESTAMP: 2025-01-14T16:30:00Z
@FEATURE_IMPLEMENTATION @LNCA_ENFORCEMENT

## FEATURE_IMPLEMENTATION Workflow Applied

### 1️⃣ EXPLORE [@DRY_FIRST, @SEMANTIC_SEARCH_REQUIRED]
**Search for existing implementations FIRST**

#### Existing Functions to REUSE:
```python
# ✅ navigation/timeline.py
find_message_by_uuid()      # Already navigates to UUID
get_message_sequence()       # Already extracts ranges
get_timeline_summary()       # Already summarizes

# ✅ navigation/checkpoint.py
find_current_checkpoint()    # Already finds checkpoints
_find_triggering_user()      # Already finds causes

# ✅ operations/core.py
restore_file_content()       # Already restores files
generate_file_diff()         # Already creates diffs
compare_files()              # Already compares
backup_file()                # Already backs up

# ✅ cli/cg.py
status()                     # Already implemented
log()                        # Already implemented
```

**NO DUPLICATE IMPLEMENTATIONS!**

### 2️⃣ RESEARCH_FIRST [@FRAMEWORK_FIRST, @DRY_FIRST]
**Verify frameworks can do everything**

#### Framework Capabilities Confirmed:
- ✅ **DuckDB**: Reads JSONL natively with SQL
- ✅ **Typer**: All CLI commands supported
- ✅ **Rich**: Tables and formatting ready
- ✅ **difflib**: Unified diff generation
- ✅ **pathlib**: File operations
- ✅ **more-itertools**: Sequence operations

**FRAMEWORK CAN DO 100%!**

### 3️⃣ PLAN [@LOC_ENFORCEMENT, @SINGLE_SOURCE_TRUTH]
**Design with <80 LOC per file**

#### File Structure (SINGLE_SOURCE_TRUTH):
```
storage/
  jsonl_engine.py    # <80 LOC - ONLY DuckDB queries

cli/
  cg.py              # Extend existing file

# NO NEW FILES IN navigation/ - REUSE ONLY!
# NO NEW FILES IN operations/ - REUSE ONLY!
```

#### Each Command <80 LOC:
```python
# cg checkout - 15 LOC
@app.command()
def checkout(target: str = typer.Argument(None)):
    """Git-like checkout"""
    session = load_latest_session()

    if Path(target).exists():  # File checkout
        checkpoint = find_current_checkpoint(session)
        content = query_jsonl(get_jsonl_path(session),
                             f"WHERE uuid = '{checkpoint['uuid']}'")
        restore_file_content(target, content)
    else:  # UUID checkout
        files = query_jsonl(get_jsonl_path(session),
                           f"WHERE uuid <= '{target}' AND name IN ('Write','Edit')")
        for f in files:
            restore_file_content(f['path'], f['content'])

# cg reset - 12 LOC
@app.command()
def reset(uuid: str, hard: bool = False):
    """Git-like reset"""
    if hard:
        # Same as checkout UUID
        checkout(uuid)
    # Soft just updates pointer (no files)

# cg revert - 10 LOC
@app.command()
def revert(uuid: str):
    """Git-like revert"""
    msg = find_message_by_uuid(session, uuid)
    if msg['toolUseResult']:
        # Restore previous state
        old = msg['toolUseResult']['oldString']
        restore_file_content(msg['file'], old)
```

### 4️⃣ USER_APPROVAL [@USER_APPROVAL]
**⚠️ BLOCKING: Cannot proceed without approval!**

```yaml
APPROVAL_CHECKLIST:
- [ ] User confirms git-like UX is correct
- [ ] User approves REUSE of existing functions
- [ ] User approves DuckDB for JSONL queries
- [ ] User approves <80 LOC per command
```

**WAITING FOR: "approved" or "proceed"**

### 5️⃣ FRAMEWORK_FIRST [@FRAMEWORK_FACADE]
**100% delegation patterns**

```python
# storage/jsonl_engine.py - ONLY framework calls
import duckdb

def query_jsonl(path: str, where: str = "") -> pd.DataFrame:
    """Pure DuckDB - no custom logic"""
    return duckdb.sql(f"SELECT * FROM '{path}' {where}").df()

def get_file_content_at(path: str, uuid: str, file: str) -> str:
    """Pure SQL - no loops or logic"""
    return duckdb.sql(f"""
        SELECT toolUseResult->>'content'
        FROM '{path}'
        WHERE uuid < '{uuid}'
          AND toolUseResult->>'filePath' = '{file}'
        ORDER BY timestamp DESC
        LIMIT 1
    """).fetchone()[0]
```

### 6️⃣ TDD_REAL_DATA [@TDD_REAL_DATA]
**Test with THIS conversation**

```python
def test_checkout_restores_memory_map():
    """Use actual file created in THIS conversation"""
    # This conversation created memory_map.md
    original = Path("memory_map.md").read_text()

    # Corrupt it
    Path("memory_map.md").write_text("CORRUPTED")

    # Use cg to restore
    result = run(["cg", "checkout", "memory_map.md"])

    # Verify restored
    assert "@NEURAL_TIMESTAMP" in Path("memory_map.md").read_text()
    assert "CORRUPTED" not in Path("memory_map.md").read_text()
```

### 7️⃣ RED [@MAINTAINER_MINDSET]
**Write failing tests first**

```python
def test_cg_checkout_not_implemented():
    """RED: This will fail until implemented"""
    result = run(["cg", "checkout", "test.py"])
    assert result.returncode == 0  # Will fail!

def test_cg_reset_not_implemented():
    """RED: This will fail until implemented"""
    result = run(["cg", "reset", "--hard", "uuid"])
    assert result.returncode == 0  # Will fail!
```

### 8️⃣ GREEN [@LOC_ENFORCEMENT, @FRAMEWORK_FIRST]
**Make tests pass with <80 LOC**

Implement each command following the PLAN phase design.

### 9️⃣ COMMIT [@VALIDATE, @LIVING_DOC_UPDATE]
**Update documentation and memory**

- Update memory_map.md with implementation status
- Update living_document.md with decisions
- Validate all commands work with real data
- Clean up any test files

## 🚫 PREVENTIVE PLANNING Applied

### Check existing files before creating (EXPLORE phase) ✅
- Found: navigation/timeline.py has UUID navigation
- Found: operations/core.py has file restoration
- Decision: REUSE, don't recreate

### Design with LOC limits in mind (PLAN phase) ✅
- Each command: 10-15 LOC max
- jsonl_engine.py: <30 LOC total
- No files will exceed 80 LOC

### Plan reusable interfaces before implementation ✅
- query_jsonl() - reusable for all JSONL queries
- Existing interfaces sufficient for all needs

## ⏸️ CURRENT STATUS: AWAITING USER_APPROVAL

Cannot proceed to TDD/implementation without explicit approval.
The @USER_APPROVAL tag enforces this block.

Say "approved" or "proceed" to continue to implementation phase.