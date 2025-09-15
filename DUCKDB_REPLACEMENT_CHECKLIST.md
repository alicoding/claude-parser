# DuckDB Complete Replacement Checklist

## Files to be REPLACED/DELETED

### Data Loading
- [ ] `session/core.py` - Polars JSONL loading → DuckDB
- [ ] Remove: `pl.read_ndjson()`, `df.to_dicts()`
- [ ] Remove: `extract_message_types()`, `extract_session_metadata()`

### Navigation & Boundaries  
- [ ] `navigation/session_boundaries.py` - Manual loops → SQL
- [ ] Remove: `enumerate()`, list comprehensions
- [ ] Replace with: SQL window functions

### Token Counting
- [ ] `tokens/status.py` - Partial counting → Complete counting
- [ ] Fix: Include user messages, tools, hooks
- [ ] Remove: Manual sum() loops

### Billing
- [ ] `analytics/billing.py` - litellm (buggy) → DuckDB
- [ ] Remove: litellm dependency
- [ ] Add: Hardcoded pricing table + SQL

### Message Filtering
- [ ] `filtering/` - Manual filtering → SQL WHERE
- [ ] `analytics/core.py` - Manual aggregations → SQL GROUP BY

### Models
- [ ] `models/message.py` - Remove business logic
- [ ] Remove: `get_token_usage()` method
- [ ] Keep: Pure data fields only

### Timeline/Navigation
- [ ] `navigation/timeline.py` - Manual search → SQL
- [ ] `navigation/checkpoint.py` - Manual detection → SQL

## Dependencies to REMOVE
- [ ] Polars
- [ ] litellm (buggy with Claude 4.x)
- [ ] more-itertools (replaced by SQL)

## New Structure - @SINGLE_SOURCE_TRUTH

```
claude_parser/
├── storage/
│   └── engine.py         # ONLY file that imports DuckDB (<80 LOC)
├── api/                  # Public API - NO DuckDB imports!
│   ├── __init__.py       # Exports public functions
│   ├── session.py        # Calls engine.query("load_session")
│   ├── tokens.py         # Calls engine.query("count_tokens")
│   └── billing.py        # Calls engine.query("calculate_cost")
```

## Critical Architecture Rules

### @SINGLE_SOURCE_TRUTH - DuckDB Isolation
- **ONLY `storage/engine.py` imports duckdb**
- All other files call `engine.query(operation, params)`
- If we need to switch from DuckDB to something else, only ONE file changes

### @DIP (Dependency Inversion Principle)
```python
# storage/engine.py - The ONLY file with DuckDB
class DataEngine:
    def query(self, operation: str, params: dict) -> Any:
        """Single interface for ALL data operations"""
        queries = {
            'load_session': self._load_session_sql,
            'count_tokens': self._count_tokens_sql,
            'calculate_cost': self._calculate_cost_sql,
            'find_boundaries': self._find_boundaries_sql,
        }
        return self._execute(queries[operation], params)

# api/tokens.py - No DuckDB knowledge!
def token_status():
    engine = DataEngine()
    return engine.query('count_tokens', {'file': get_current_file()})
```

### @DRY - No SQL duplication
- All SQL queries in ONE place (inside engine.py)
- No SQL strings in any other file
- Operations identified by name, not SQL

## SQL Queries Needed

1. **Load Session**
```sql
SELECT * FROM read_json_auto(?) ORDER BY rowid
```

2. **Session Boundaries**
```sql
WITH boundaries AS (
  SELECT MAX(rowid) as last_compact
  FROM read_json_auto(?)
  WHERE json_extract(data, '$.isCompactSummary') = true
)
SELECT * FROM read_json_auto(?)
WHERE rowid > COALESCE((SELECT last_compact FROM boundaries), 0)
```

3. **Token Counting (Complete)**
```sql
SELECT 
  -- Assistant messages with usage data
  SUM(CASE 
    WHEN type = 'assistant' AND json_valid(message.usage)
    THEN json_extract(message.usage, '$.input_tokens') + 
         json_extract(message.usage, '$.output_tokens')
    -- All other messages: estimate from content
    ELSE LENGTH(COALESCE(content, '')) / 4
  END) as context_tokens
FROM read_json_auto(?)
```

4. **Billing Calculation**
```sql
SELECT
  SUM(json_extract(message.usage, '$.input_tokens')) * 3.0/1000000 as input_cost,
  SUM(json_extract(message.usage, '$.output_tokens')) * 15.0/1000000 as output_cost,
  SUM(json_extract(message.usage, '$.cache_read_input_tokens')) * 0.3/1000000 as cache_cost
FROM read_json_auto(?)
WHERE type = 'assistant'
```

5. **Message Filtering**
```sql
SELECT * FROM read_json_auto(?)
WHERE type = ? 
  AND NOT (content LIKE '%hook>%')
  AND json_extract(data, '$.isVisible') != false
```

## Testing Requirements

- [ ] All tests use public API only
- [ ] No imports from internal modules
- [ ] Use real JSONL files
- [ ] Test token counts match UI
- [ ] Test billing calculations
- [ ] Test session boundaries

## Success Metrics

1. **Code Reduction**: 500+ lines → <200 lines
2. **File Reduction**: 15+ files → 5 files  
3. **Dependency Reduction**: 5+ libs → 2 (DuckDB + genson)
4. **Performance**: 10x faster on large files
5. **Accuracy**: Token counts match UI exactly
6. **Maintainability**: 1 place to update for changes

## Migration Order

1. Create DuckDB engine with genson
2. Write SQL queries for all operations
3. Create blackbox tests
4. Replace one module at a time
5. Verify tests still pass
6. Remove old code
7. Remove unused dependencies

## Rollback Plan

- Keep old code in `legacy/` folder initially
- Feature flag to switch implementations
- Benchmark both implementations
- Only delete after 1 week stable