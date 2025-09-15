# DuckDB Migration Plan - 100% LNCA Compliance

## Current Architecture Audit

### 🔍 Framework Delegation Analysis

#### session/core.py [@FRAMEWORK_FIRST, @SINGLE_SOURCE_TRUTH]
**Current**: Polars for JSONL loading
**Issues**: 
- ✅ Good: 100% Polars delegation
- ❌ Violation: `df.to_dicts()` then manual loop for RichMessage creation
- ❌ Violation: Polars adds `None` for missing fields (schema normalization issue)

#### models/message.py [@DATA_DRIVEN, @BOUNDED_CONTEXT_ISOLATION]
**Current**: Pydantic for data modeling
**Issues**:
- ✅ Good: Pure data structure
- ❌ Violation: `get_token_usage()` has extraction logic (should be pure data)
- ❌ Violation: `@property def model` - computed property mixing concerns

#### navigation/session_boundaries.py [@FRAMEWORK_BYPASS_CLEANUP]
**Current**: Manual loops for finding boundaries
**Issues**:
- ❌ Major violation: Manual enumerate() and list comprehension
- ❌ Should use framework (more-itertools or SQL)

#### tokens/status.py [@SINGLE_SOURCE_TRUTH]
**Current**: Mixed - some framework, some manual
**Issues**:
- ✅ Good: Uses sum() generator
- ❌ Violation: Imports internal modules not in public API
- ❌ Violation: Manual message filtering

#### analytics/billing.py [@FRAMEWORK_FACADE]
**Current**: litellm for cost calculation
**Issues**:
- ✅ Good: Delegates to litellm
- ❌ Bug: Negative costs with Claude 4.x models
- ❌ Violation: Manual message filtering

## DuckDB Migration Architecture

### 🎯 @SINGLE_SOURCE_TRUTH Design

```
claude_parser/
├── storage/
│   └── duckdb_engine.py  # ONE place for ALL data operations
├── models/
│   └── message.py         # Pure data structures ONLY
├── api/
│   ├── tokens.py          # Public API wrapping storage
│   ├── billing.py         # Public API wrapping storage
│   └── navigation.py      # Public API wrapping storage
```

### Core Principles

#### 1. @SINGLE_SOURCE_TRUTH
```python
# storage/duckdb_engine.py - ALL data operations here
class DuckDBEngine:
    """Single source of truth for ALL data operations"""
    
    def query_tokens_in_session(self, file_path: str) -> int:
        """SQL replaces manual loops"""
        return self.conn.execute("""
            WITH session_bounds AS (
                SELECT MAX(rowid) as last_compact 
                FROM read_json_auto(?) 
                WHERE "$.isCompactSummary" = true
            )
            SELECT SUM(
                "$.message.usage.input_tokens" + 
                "$.message.usage.output_tokens"
            )
            FROM read_json_auto(?)
            WHERE rowid > COALESCE(
                (SELECT last_compact FROM session_bounds), 0
            )
        """, [file_path, file_path]).fetchone()[0]
```

#### 2. @FRAMEWORK_FIRST
- DuckDB handles ALL: loading, filtering, aggregation, joins
- No manual loops, no Python data processing
- SQL window functions for session boundaries

#### 3. @API_FIRST_TEST_DATA
```python
# Public API unchanged
from claude_parser import token_status, calculate_session_cost

# Implementation swapped internally
status = token_status()  # Now uses DuckDB
cost = calculate_session_cost()  # Now uses DuckDB
```

#### 4. @TEST_DATA_BYPASS_ANTIPATTERN Prevention
```python
# tests/test_token_status.py
def test_token_counting():
    """Blackbox test - only public API"""
    status = token_status()
    assert 'current' in status
    assert 'limit' in status
    # NO internal imports, NO mocking
```

## Migration Steps

### Phase 1: Create DuckDB Engine [@FRAMEWORK_FACADE]
1. Create `storage/duckdb_engine.py` (<80 LOC)
2. Implement core queries:
   - load_session()
   - find_session_boundaries()  
   - calculate_tokens()
   - calculate_billing()

### Phase 2: Update Models [@BOUNDED_CONTEXT_ISOLATION]
1. Remove `get_token_usage()` from RichMessage
2. Make models pure data (no logic)
3. Move extraction to DuckDB queries

### Phase 3: Refactor APIs [@SINGLE_SOURCE_TRUTH]
1. `tokens/status.py` → Delegate to DuckDB
2. `analytics/billing.py` → Delegate to DuckDB
3. Remove all manual loops

### Phase 4: Blackbox Testing [@TDD_REAL_DATA]
1. Test ONLY public API
2. Use real JSONL files
3. No mocking, no internal imports

## Benefits of DuckDB

### 1. @FRAMEWORK_FIRST Victory
```sql
-- Replace 50+ lines of Python with 5 lines of SQL
SELECT 
    SUM(CASE WHEN cache THEN tokens * 0.1 ELSE tokens END) as cost
FROM messages
WHERE session_id = current_session()
```

### 2. @SINGLE_SOURCE_TRUTH Victory
- ONE place for schema knowledge (DuckDB)
- ONE place for aggregations (SQL)
- ONE place for filtering (WHERE clauses)

### 3. @NO_VARIANT_NAMING Victory
- DuckDB handles camelCase/snake_case automatically
- JSON path expressions handle nested fields
- No Pydantic alias complexity

### 4. Performance Benefits
- No loading entire JSONL into memory
- Streaming processing
- Built-in caching
- Parallel query execution

## Anti-Pattern Prevention

### ❌ @FRAMEWORK_BYPASS_CLEANUP
Before: Manual loops everywhere
After: 100% SQL delegation

### ❌ @MANUAL_PARSING_ANTIPATTERN  
Before: Regex/string parsing for fields
After: JSON path expressions in SQL

### ❌ @TEST_DATA_BYPASS_ANTIPATTERN
Before: Testing internals
After: Blackbox API testing only

### ❌ @IMPORT_FALLBACK_ANTIPATTERN
Before: Importing internal modules
After: Public API only

## Success Metrics

1. **LOC Reduction**: ~500 lines → ~200 lines
2. **Framework Delegation**: 100% SQL, 0% manual loops
3. **Test Coverage**: 100% blackbox tests
4. **Performance**: 10x faster for large files
5. **Maintainability**: 1 place to update for schema changes

## Implementation Order

1. **RESEARCH_FIRST**: Study DuckDB JSON capabilities
2. **FRAMEWORK_FIRST**: Create DuckDB engine
3. **TDD_REAL_DATA**: Write blackbox tests first
4. **RED**: Tests fail with current implementation
5. **GREEN**: Swap to DuckDB, tests pass
6. **REFACTOR**: Remove old Polars/manual code
7. **VALIDATE**: Performance benchmarks
8. **COMMIT**: Update living document

## Risk Mitigation

1. **Schema Changes**: DuckDB handles gracefully with JSON paths
2. **Missing Fields**: COALESCE() and NULL handling in SQL
3. **Performance**: Use indexes on JSONL if needed
4. **Compatibility**: Keep public API unchanged

## @LIVING_DOC_UPDATE Requirements

Document:
- SQL queries for each operation
- Performance benchmarks
- Schema evolution handling
- Migration rollback plan