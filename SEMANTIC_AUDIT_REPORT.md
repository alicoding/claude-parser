# Semantic Search Audit Report - claude-parser v2.0.0
Generated: 2025-09-16T02:30:00Z
Tool: semantic-search MCP service

## Executive Summary
- **Total Violations Found**: 30
- **Critical Security Issues**: 1 (test credentials in production)
- **Architecture Violations**: 25
- **Dead Code Modules**: ~10 empty directories
- **Coverage Impact**: Dead code artificially lowering coverage from ~60% to 43%

## Critical Issues (Fix Immediately)

### 1. 🚨 **Test Credentials in Production**
```python
# test_folder/config/settings.py - SHIPPED TO USERS!
DEBUG = True
API_KEY = "test-key-12345"
DATABASE_URL = "sqlite:///test.db"
```
**Risk**: HIGH - Exposed test credentials in PyPI package
**Fix**: Delete entire test_folder from production

### 2. 🚨 **Test Files in Root Directory**
```
test_single.py          # Test file at root
verify_spec.py          # Verification script
test_folder/            # Entire test directory
test_archive/           # Archive directory
```
**Risk**: MEDIUM - Unnecessary files increasing package size
**Fix**: Move to tests/ or delete entirely

## Architecture Violations by Pattern

### @CUSTOM_CODE_ANTIPATTERN (5 files)
Files implementing custom logic instead of using framework APIs:

| File | Issue | Suggested Fix |
|------|-------|--------------|
| hooks/handlers.py | Lambda handlers with custom logic | Use Typer commands directly |
| hooks/executor.py | Manual execution flow | Use framework's built-in executor |
| test_single.py | Should not exist in production | Delete |
| verify_spec.py | Should not exist in production | Delete |

### @FRAMEWORK_BYPASS (5 files)
Direct library imports instead of using facades:

| File | Direct Import | Should Use |
|------|---------------|------------|
| hooks/request.py | `import json` directly | Use pydantic for JSON |
| analytics/core.py | Direct pandas usage | Use polars (already in deps) |
| queries/session_queries.py | Direct DuckDB SQL | Use query builder |

### @LOC_ENFORCEMENT (5 potential violations)
Files potentially exceeding 80 lines:

| File | Status | Action |
|------|--------|--------|
| models/__init__.py | Need to verify | Check actual LOC |
| hooks/handlers.py | Need to verify | Split if >80 |
| hooks/app.py | Need to verify | Split if >80 |

### @UTIL_FIRST_VIOLATION (5 files)
Creating custom utilities without checking for existing ones:

| File | Custom Utility | Existing Alternative |
|------|----------------|---------------------|
| hooks/extraction.py | Custom dict extraction | Use glom |
| operations/core.py | File operations | Use pathlib |
| hooks/handlers.py | Response handling | Use Typer |

### @DRY_VIOLATION_ANTIPATTERN (5 files)
Duplicate logic across files:

| Duplicate Pattern | Files | Extract To |
|-------------------|-------|------------|
| Hook event handling | handlers.py, app.py | Single handler |
| File operations | diff_ops.py, file_ops.py | Unified ops |
| Session loading | Multiple files | Single loader |

## Dead Code Analysis

### Empty/Unused Directories
```
claude_parser/
├── domain/           # EMPTY - only __pycache__
│   ├── delegates/    # EMPTY
│   ├── entities/     # EMPTY
│   ├── filters/      # EMPTY
│   ├── interfaces/   # EMPTY
│   ├── services/     # EMPTY
│   └── value_objects/# EMPTY
├── application/      # LIKELY UNUSED
├── infrastructure/   # LIKELY UNUSED
└── utils/           # LIKELY UNUSED
```

### Unused Modules (0% coverage)
- analytics/billing.py
- analytics/litellm_adapter.py
- Several others with <20% coverage

## Remediation Plan

### Phase 1: Critical Security (v2.0.1) - TODAY
```bash
# 1. Remove test files from production
rm -rf test_folder/ test_archive/ test_single.py verify_spec.py

# 2. Clean git history (remove sensitive data)
git filter-branch --tree-filter 'rm -rf test_folder' HEAD

# 3. Release v2.0.1 immediately
./publish.sh  # Bump to 2.0.1
```

### Phase 2: Clean Architecture (v2.1.0) - This Week
```bash
# 1. Remove empty domain folders
rm -rf claude_parser/domain/
rm -rf claude_parser/application/
rm -rf claude_parser/infrastructure/
rm -rf claude_parser/utils/

# 2. Fix framework bypasses
# - Replace direct imports with facades
# - Use existing libraries (glom, polars, etc.)

# 3. Extract duplicate logic
# - Create single hook handler
# - Unify file operations
```

### Phase 3: Improve Coverage (v2.2.0) - Next Week
```bash
# 1. Remove dead code from coverage calculation
# 2. Add black box tests for actual API
# 3. Target: 80% coverage of USED code
```

## Validation Checklist

Before proceeding, validate:
- [ ] Confirm test_folder/ contains no production code
- [ ] Verify domain/ folders are truly empty
- [ ] Check if any imports reference deleted modules
- [ ] Ensure CI/CD still passes after cleanup
- [ ] Confirm package still installs correctly

## Commands to Validate

```bash
# Check what's actually imported
grep -r "from claude_parser.domain" claude_parser/
grep -r "from claude_parser.application" claude_parser/
grep -r "from claude_parser.infrastructure" claude_parser/

# Check file sizes
find claude_parser -name "*.py" -exec wc -l {} \; | sort -rn | head -20

# Test package without dead code
pip install -e .
python -c "from claude_parser import load_session; print('✅')"
```

## Next Steps

1. **Review this report** with semantic-search findings
2. **Validate** each finding manually
3. **Execute Phase 1** immediately (security fix)
4. **Plan Phase 2** based on validation results
5. **Track progress** in this document

## Metrics to Track

| Metric | Current | Target | After Cleanup |
|--------|---------|--------|---------------|
| Package Size | ? MB | <1 MB | TBD |
| File Count | 64 | <40 | TBD |
| Coverage | 43.77% | 80% | TBD |
| Violations | 30 | 0 | TBD |
| Dead Folders | ~10 | 0 | TBD |

---
*This audit was generated using semantic-search MCP service - first production use*