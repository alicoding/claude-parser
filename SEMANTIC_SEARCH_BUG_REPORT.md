# Semantic Search Bug Report
**Date**: 2025-09-15T03:00:00Z
**Reporter**: claude-parser v2.0.1 team
**Service**: semantic-search MCP

## Bug Summary
Semantic search fails to find conceptually related code patterns, returning keyword-matched but semantically unrelated files.

## Reproduction Steps

1. Query: `"black box test real data API test integration"`
2. Expected: Test files, test patterns, testing utilities
3. Actual: Random files with keywords but no semantic relevance

## Actual Results Returned

```python
# Query: "black box test real data API test integration"
1. test_single.py - "Hello World" print statement (NOT a test)
2. main.py - Basic main function (NOT a test)
3. verify_spec.py - Empty file (0 bytes)
4. settings.py - Test credentials we're trying to REMOVE
5. analytics/__init__.py - Module init (unrelated)
```

## Expected Behavior
Should return files that are semantically related to testing:
- Actual test files (test_*.py)
- Test fixtures and utilities
- Testing patterns and frameworks
- Black box testing examples

## Root Cause Analysis
The service appears to use literal keyword matching rather than semantic understanding:
- Matches "test" in filename regardless of content
- Doesn't understand "black box testing" as a concept
- Returns files with ANY matching keyword, not conceptual relevance

## Impact
- @SEMANTIC_SEARCH_REQUIRED pattern becomes unreliable
- Cannot find existing patterns before writing code
- Violates @DRY_FIRST and @UTIL_FIRST enforcement
- Forces manual searching instead of automated discovery

## Suggested Fix
1. Use embeddings that understand testing concepts
2. Weight actual test files higher (test_*.py pattern)
3. Consider file structure context (tests/ directory)
4. Understand testing terminology (black box, unit, integration)

## Workaround
Currently using grep/fd for literal searches instead of semantic search for testing patterns.

## Severity
**HIGH** - Core LNCA pattern (@SEMANTIC_SEARCH_REQUIRED) is compromised

## Additional Bugs Found (2025-01-15)

### MCP Tool Timeout Issues
**Detected**: 2025-01-15T21:00:00Z
**Issue**: find_violations() timing out after 5 seconds
**Fix Applied**: Added 30s timeout to httpx.AsyncClient
**Status**: RESOLVED

### CWD Context Not Auto-Detected
**Detected**: 2025-01-15T20:45:00Z
**Issue**: MCP tools required explicit project parameter when already in project directory
**Fix Applied**: Added os.getcwd() fallback to auto-detect project from CWD
**Status**: RESOLVED
**Files Changed**:
- mcp_server.py:115-138 (find_violations, check_architecture_compliance)

## Test Case for Verification
```python
# This query should return test files, not random files:
results = discover_code_patterns("black box testing pattern example")
assert any("test_" in r['file_name'] for r in results)
assert not any("settings.py" in r['file_name'] for r in results)
```

---
*Filed per @IMMEDIATE_ALERT and @SEMANTIC_SEARCH_BUGS patterns*