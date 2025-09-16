# Semantic Search Bug Report for Fixing
**Date**: 2025-09-15T03:35:00Z
**Reporter**: claude-parser team (first production dogfooding)
**For**: semantic-search Claude Code session to fix

## 🔴 Critical Bugs Found

### Bug 1: Keyword Matching Instead of Semantic Understanding
**Severity**: HIGH
**Impact**: Core functionality broken - not doing "semantic" search

#### Reproduction
```python
from mcp_semantic_search import discover_code_patterns

# Search for testing patterns
results = discover_code_patterns("black box test real data API test integration")

# EXPECTED: Test files, test utilities, testing patterns
# ACTUAL: Random files with word "test" in them:
#   - test_single.py (not a test, just has "test" in name)
#   - settings.py (has "test" credentials)
#   - empty verify_spec.py (0 bytes)
#   - analytics/__init__.py (unrelated)
```

#### Root Cause
The embeddings appear to be doing keyword matching rather than understanding concepts:
- Matches ANY file with "test" in filename
- Doesn't understand "black box testing" as a concept
- Returns files with matching keywords but no semantic relevance

#### Fix Needed
1. Use code-aware embeddings (like CodeBERT or similar)
2. Weight actual test files (test_*.py pattern) higher
3. Understand testing terminology semantically
4. Consider file structure (tests/ directory should rank higher)

---

### Bug 2: Timeout Issues (RESOLVED but worth noting)
**Severity**: MEDIUM (was HIGH)
**Status**: Fixed locally but not in main branch?

#### What Was Fixed
- Added 30s timeout to httpx.AsyncClient
- Issue: find_violations() was timing out after 5 seconds

#### Location of Fix
- File: mcp_server.py:115-138
- Functions: find_violations(), check_architecture_compliance()

---

### Bug 3: CWD Context Not Auto-Detected (RESOLVED)
**Severity**: LOW
**Status**: Fixed locally

#### What Was Fixed
- MCP tools required explicit project parameter even when in project directory
- Added os.getcwd() fallback to auto-detect project from CWD

---

## 🟡 Accuracy Issues Found

### Issue 1: Mixed Accurate and Inaccurate Results
The audit returned a mix of:
- ✅ **ACCURATE**: Empty domain folders (verified and deleted)
- ✅ **ACCURATE**: filters.py with 82 lines (LOC violation, now fixed)
- ❓ **QUESTIONABLE**: Some test files that may not have existed
- ❌ **WRONG**: Returned files based on keyword not semantic meaning

### Issue 2: Pattern Detection Limitations
**Query**: "find violations"
**Expected**: Find LNCA pattern violations
**Actual**: Found some real violations but also false positives

---

## 📊 Test Cases for Verification

### Test 1: Semantic Understanding
```python
def test_semantic_understanding():
    # Should understand concepts, not keywords
    results = discover_code_patterns("testing patterns for black box")

    # Should return actual test files
    assert any("test_" in r['file_name'] for r in results)

    # Should NOT return non-test files with "test" in name
    assert not any("settings.py" in r['file_name'] for r in results)
```

### Test 2: Code-Aware Search
```python
def test_code_aware_search():
    # Should understand code patterns
    results = discover_code_patterns("singleton pattern implementation")

    # Should find actual singleton implementations
    # Not just files with word "singleton"
```

### Test 3: Architecture Pattern Search
```python
def test_architecture_patterns():
    # Should find LNCA violations
    results = find_violations(project="claude-parser")

    # Should identify:
    # - Files >80 LOC
    # - Custom code instead of framework delegation
    # - DRY violations
```

---

## 💡 Suggestions for Improvement

### 1. Use Code-Specific Embeddings
- Current: General text embeddings
- Needed: Code-aware models like:
  - CodeBERT
  - GraphCodeBERT
  - CodeT5
  - Or OpenAI's code-specific embeddings

### 2. Add Pattern Recognition
```python
# Recognize common patterns
PATTERNS = {
    "test": r"test_*.py",
    "fixture": r"*fixture*.py",
    "mock": r"*mock*.py",
    "config": r"*config*.py|*settings*.py"
}
```

### 3. Weight File Structure
```python
def score_result(file_path, query):
    score = base_embedding_score

    # Boost test files for test queries
    if "test" in query and "test_" in file_path:
        score *= 1.5

    # Boost files in tests/ directory
    if "test" in query and "/tests/" in file_path:
        score *= 1.3

    return score
```

### 4. Add Semantic Context
- Include file imports in embeddings
- Include function signatures
- Include class hierarchies
- Include docstrings

---

## 🔄 Dogfooding Benefits

This is the FIRST production use of semantic-search and we found:
1. Real bugs that need fixing
2. Accuracy issues to improve
3. Feature gaps to fill

The dogfooding cycle:
- **semantic-search** → finds violations in **claude-parser**
- **claude-parser** → parses conversations for **semantic-search**
- Both improve through real use

---

## 📝 Priority Order for Fixes

1. **CRITICAL**: Fix keyword matching → implement semantic understanding
2. **HIGH**: Add code-aware embeddings
3. **MEDIUM**: Improve pattern recognition
4. **LOW**: Add file structure weighting

---

## 🧪 How to Test Your Fixes

After implementing fixes, test with claude-parser:
```bash
cd /Volumes/AliDev/ai-projects/claude-parser

# Run the audit again
python -c "
from semantic_search import find_violations
violations = find_violations()
print(f'Found {len(violations)} violations')
"

# Test semantic understanding
python -c "
from semantic_search import discover_code_patterns
results = discover_code_patterns('black box testing patterns')
# Should return actual test files, not random files
"
```

---

## 📌 Remember

This bug report is part of the dogfooding cycle. Fix these bugs and claude-parser will:
1. Better analyze your conversations
2. Find more bugs for you to fix
3. Create a virtuous improvement cycle

Good luck with the fixes! 🚀