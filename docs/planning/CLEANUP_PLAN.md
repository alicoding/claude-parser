# 🚨 SAFE CLEANUP PLAN - ZERO RISK APPROACH

## Current Status: 3/6 Pipeline Checks Passing (50%)

### ✅ Already Passing:
1. API Contract Tests (11/12)
2. Test Coverage (92.86%)
3. Ruff Linting (0 errors)

### ❌ Blocking Issues:
1. 28 Python files in root (should be organized)
2. 30+ forbidden import violations
3. 14 files over 150 LOC limit

## 📋 PHASED APPROACH (Zero Risk)

### PHASE 1: Safe Cleanup (NO CODE CHANGES)
**Risk Level: ZERO** - Just moving files, no logic changes

#### 1.1 Create Proper Directories
```bash
mkdir -p scripts/experiments  # For ad-hoc test scripts
mkdir -p scripts/research     # For research scripts  
mkdir -p scripts/security     # For security tools
mkdir -p scripts/violations   # For violation test files
```

#### 1.2 Move Files (Not Imported Anywhere)
```bash
# Move ad-hoc test scripts (7 files)
mv test_parse_debug.py scripts/experiments/
mv test_discovery_tdd.py scripts/experiments/
mv test_parse_with_module.py scripts/experiments/
mv test_parse_line.py scripts/experiments/
mv test_real_conversation_navigation.py scripts/experiments/
mv test_discovery.py scripts/experiments/
mv test_strict.py scripts/experiments/

# Move research scripts (4 files)
mv research_*.py scripts/research/

# Move violation test files (6 files - created only to test hooks)
mv test_violations.py scripts/violations/
mv test_hook*.py scripts/violations/
mv violation_demo.py scripts/violations/
mv demo_violations.py scripts/violations/

# Move security utilities (2 files)
mv clean_secrets.py scripts/security/
mv security_scan.py scripts/security/

# Move other utilities
mv library_research.py scripts/research/
mv debug_parse_errors.py scripts/experiments/
```

**DO NOT MOVE YET:**
- `verify_spec.py` - Pipeline depends on it being in root

### PHASE 2: Fix Forbidden Imports (WITH TESTING)
**Risk Level: LOW** - Simple replacements, but test each change

#### 2.1 Test API Compatibility First
```python
# Create test_library_compatibility.py
import orjson
import json

# Verify orjson.dumps() == json.dumps() for our use cases
# Verify orjson.loads() == json.loads() for our use cases
```

#### 2.2 Fix Priority Files (in claude_parser/)
These are REAL code, fix carefully:
1. `claude_parser/watch_async.py` - import json → orjson
2. `claude_parser/application/sse_service.py` - import json → orjson

#### 2.3 Fix Test Files (Low Priority)
Files in scripts/violations/ can use forbidden imports (they're testing violations!)

### PHASE 3: Split Oversized Files (TDD APPROACH)
**Risk Level: MEDIUM** - Must maintain interfaces

#### Files to Split (Using Libraries):
1. **analyzer.py** (303 → <150 lines)
   - Extract TokenCounter class → `domain/services/token_counter.py`
   - Extract StatsCalculator → `domain/services/stats_calculator.py`
   - Use pandas for data analysis instead of manual code

2. **transcript_finder.py** (263 → <150 lines)
   - Use pathlib.rglob() instead of manual recursion
   - Use toolz for all filtering
   - Extract search logic to separate service

3. **jsonl_parser.py** (252 → <150 lines)
   - Already uses orjson (good!)
   - Extract validation to `domain/validators/jsonl_validator.py`
   - Use more-itertools for streaming

### PHASE 4: Consolidate verify_spec.py
**Risk Level: HIGH** - Pipeline depends on this

#### 4.1 Document Current Checks
```python
# Document what verify_spec.py currently checks:
# 1. Forbidden imports
# 2. File sizes
# 3. Pydantic models
# 4. Test coverage
```

#### 4.2 Create Unified Version
1. Keep in root (where pipeline expects it)
2. Merge best features from verify_spec_v2.py
3. Test extensively before removing v2

### PHASE 5: Set Up Enforcement
**Risk Level: LOW** - Using pre-commit framework

#### 5.1 Create .pre-commit-config.yaml
```yaml
repos:
  # Use ruff for linting/formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
      - id: ruff-format

  # Block forbidden imports
  - repo: https://github.com/pre-commit/pygrep-hooks
    rev: v1.10.0
    hooks:
      - id: python-check-blanket-noqa
      - id: python-no-eval

  # Custom checks
  - repo: local
    hooks:
      - id: forbidden-imports
        name: Check forbidden imports
        entry: python scripts/check_forbidden_imports.py
        language: system
        types: [python]
        
      - id: file-size-check
        name: Check file sizes
        entry: python scripts/check_file_size.py
        language: system
        types: [python]
```

## 🎯 Success Metrics

After each phase, verify:
1. `pytest tests/test_api_contract.py` - Still 11/12 passing
2. `pytest --cov` - Coverage still >90%
3. `python verify_spec.py` - More checks passing
4. `ruff check claude_parser/` - No new errors

## ⚠️ CRITICAL RULES

### DO NOT:
- Delete ANY file without checking imports
- Move verify_spec.py (pipeline needs it in root)
- Change ANY logic without tests
- Use manual code instead of libraries

### ALWAYS:
- Test after EVERY change
- Use git commits after each successful phase
- Check AI_CONTEXT.md for proper file placement
- Use libraries (95/5 principle)

## 📊 Expected Outcome

| Check | Before | After |
|-------|--------|-------|
| API Contract | ✅ 11/12 | ✅ 11/12 |
| Coverage | ✅ 92.86% | ✅ >90% |
| Ruff Linting | ✅ 0 errors | ✅ 0 errors |
| Spec Verification | ❌ Many violations | ✅ All pass |
| Unused Files | ❌ 42+ files | ✅ Clean |
| File Sizes | ❌ 14 over 150 | ✅ All <150 |

**Pipeline Status: 6/6 Passing (100%)**

## 🔄 Rollback Plan

Each phase creates a git commit:
```bash
git add -A && git commit -m "Phase 1: Move test scripts to scripts/"
git add -A && git commit -m "Phase 2: Fix forbidden imports"
git add -A && git commit -m "Phase 3: Split oversized files"
# etc.
```

If anything breaks: `git reset --hard HEAD~1`

## 📝 Backlog Tasks

All tasks documented in dstask:
- Task #29: Root folder cleanup
- Task #66: Consolidate verify_spec.py
- Task #67: Fix forbidden imports
- Task #68: Pre-commit enforcement
- Task #69: Split oversized files

Run `dstask show-open --project claude-parser` to see all tasks.