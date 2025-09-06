# Claude Parser - Target Green State Contract

## 🎯 API Contract (MUST NOT BREAK)

### Core Public API (95% Use Cases)
```python
# 1. PARSER - Load conversations
from claude_parser import load, load_large, load_many
conv = load("session.jsonl")  # MUST WORK
messages = conv.messages       # MUST WORK
assistant = conv.assistant_messages  # MUST WORK

# 2. HOOKS - Handle Claude events
from claude_parser.hooks import hook_input, exit_success, exit_block
data = hook_input()  # MUST WORK
exit_success()       # MUST WORK
exit_block("reason") # MUST WORK

# 3. WATCH - Monitor files
from claude_parser.watch import watch
watch("file.jsonl", callback)  # MUST WORK
```

### Feature Registry Status (MUST MAINTAIN)
| Feature | Status | Tests | Coverage | MUST KEEP |
|---------|--------|-------|----------|-----------|
| load | ✅ complete | 15/15 | 100% | YES |
| Conversation | ✅ complete | 20/20 | 100% | YES |
| hook_input | ✅ complete | 11/11 | 100% | YES |
| exit_success | ✅ complete | 10/10 | 100% | YES |
| exit_block | ✅ complete | 10/10 | 100% | YES |
| exit_error | ✅ complete | 10/10 | 100% | YES |
| watch | ✅ complete | 4/4 | 100% | YES |
| error_filter | ✅ complete | 3/3 | 100% | YES |

## ✅ Green State Requirements

### File Structure
```
claude_parser/
├── __init__.py          # Public API exports only
├── api.py               # Main API functions (load, etc)
├── conversation.py      # ONE Conversation class (<150 LOC)
├── hooks/              # Hook domain (already good)
│   ├── __init__.py
│   ├── input.py
│   ├── exits.py
│   └── json_output.py
├── models/             # Pydantic models (no models.py file!)
│   └── *.py
├── watch/              # Watch domain (consolidate)
│   └── watcher.py      # ONE watcher implementation
└── infrastructure/     # Technical implementations
    └── parsers.py      # JSONL parsing
```

### Metrics
- **Files**: ~80 (from 141)
- **Max LOC per file**: 150
- **Test coverage**: ≥90%
- **Duplicate code**: 0%
- **Library usage**: 95%

## 🧪 Test Suite (MUST PASS)

### 1. API Compatibility Tests
```python
# tests/test_api_contract.py
def test_load_works():
    conv = load("test.jsonl")
    assert conv is not None

def test_conversation_api():
    conv = load("test.jsonl")
    assert hasattr(conv, 'messages')
    assert hasattr(conv, 'assistant_messages')
    assert hasattr(conv, 'user_messages')

def test_hooks_api():
    from claude_parser.hooks import hook_input, exit_success
    # Must import without error
```

### 2. Feature Tests (existing)
- `tests/test_conversation.py` - MUST PASS
- `tests/test_hooks.py` - MUST PASS
- `tests/test_watch.py` - MUST PASS

### 3. CI/CD Pipeline
```yaml
# .github/workflows/test.yml
- run: pytest tests/test_api_contract.py
- run: pytest tests/ --cov=claude_parser --cov-report=term
- run: python scripts/verify_spec.py
- run: make lint
```

## 🚫 Breaking Changes NOT Allowed

1. **Import paths**:
   - `from claude_parser import load` MUST WORK
   - `from claude_parser.hooks import hook_input` MUST WORK

2. **Conversation API**:
   - `.messages` property MUST EXIST
   - `.assistant_messages` property MUST EXIST
   - `.user_messages` property MUST EXIST
   - `.search()` method MUST EXIST

3. **Hook API**:
   - `hook_input()` returns HookData object
   - `exit_success/block/error` work as documented

## 📋 Consolidation Plan

### Phase 1: Delete Unused (Safe)
- [ ] Remove 13 test*.py files from root
- [ ] Remove unused research*.py files
- [ ] Remove claude_parser/conversation.py (unused)
- [ ] Remove claude_parser/models.py (use models/ dir)

### Phase 2: Merge Duplicates (Careful)
- [ ] Merge 3 Conversation classes → 1
- [ ] Merge watch implementations → 1
- [ ] Consolidate feature data files → 1

### Phase 3: Use Libraries (95/5)
- [ ] Replace 97 filter patterns with funcy
- [ ] Use attrs/pydantic consistently
- [ ] Use toolz for all functional ops

### Phase 4: Reorganize (DDD)
- [ ] Move files to proper domains
- [ ] Ensure <150 LOC per file
- [ ] Update imports in __init__.py

## 🔒 Service Request Model

Per coordination with temporal-hooks team, bug reports will be filed as service requests in backlog:

```bash
# Example service request from hooks team
dstask add "BUG: Parser blocking on large JSONL files" \
  --project claude-parser \
  --priority P0 \
  --tags bug,service-request

dstask <id> note "
REPORTED BY: temporal-hooks team
ISSUE: Parser blocks when loading 500MB+ JSONL
REPRODUCTION:
1. Load large file with load('large.jsonl')
2. Process hangs at line 45
ERROR: TimeoutError
TEST FILE: /tmp/test_large.jsonl
"
```

## ✅ Definition of Done

- [ ] All API contract tests pass
- [ ] All existing tests pass
- [ ] Coverage ≥90%
- [ ] No files >150 LOC
- [ ] No duplicate code (jscpd report clean)
- [ ] Make lint passes
- [ ] Make precommit passes
- [ ] Feature registry shows all green
- [ ] Backlog shows zero P0 bugs
