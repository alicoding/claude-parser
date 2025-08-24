# Migration Plan: Consolidate to DDD Structure

## Current State
We have duplicate functionality:
1. **Old**: `claude_parser/parser.py` - Non-DDD, has violations
2. **New**: `claude_parser/infrastructure/message_repository.py` - DDD compliant

## Functions to Migrate

### From parser.py to infrastructure/

| Function | Current Location | New Location | Purpose |
|----------|-----------------|--------------|---------|
| parse_jsonl | parser.py | infrastructure/jsonl_parser.py | Raw JSONL parsing |
| parse_jsonl_streaming | parser.py | infrastructure/jsonl_parser.py | Streaming parse |
| count_messages | parser.py | infrastructure/jsonl_parser.py | Count without loading |
| validate_jsonl | parser.py | infrastructure/jsonl_validator.py | Validate JSONL |
| validate_claude_format | parser.py | infrastructure/claude_validator.py | Validate Claude format |

## Migration Steps

1. **Create new infrastructure services**:
   - `infrastructure/jsonl_parser.py` - Pure JSONL operations
   - `infrastructure/jsonl_validator.py` - Validation operations
   
2. **Update imports in __init__.py**:
   - FROM: `from .parser import ...`
   - TO: `from .infrastructure.jsonl_parser import ...`

3. **Update all test imports**

4. **Delete old parser.py**

## Violations Found in Current Code

### parser.py (to be fixed during migration):
- Line 32: `for line_num, line in enumerate(f, 1)` - manual loop
- Line 40: `messages.append(data)` - manual append  
- Line 43: `errors.append((line_num, str(e)))` - manual append
- Line 71: `for line_num, line in enumerate(f, 1)` - manual loop
- Line 95: `for _ in parse_jsonl_streaming(filepath)` - manual loop
- Line 96: `count += 1` - manual increment
- Line 117: `for line_num, line in enumerate(f, 1)` - manual loop
- Line 125: `error_lines.append(line_num)` - manual append
- Line 154: `for i, msg in enumerate(parse_jsonl_streaming(filepath))` - manual loop
- Line 155: `messages.append(msg)` - manual append
- Line 185-195: Multiple `for` loops for signatures and types
- Line 211-213: `for msg in messages` - manual loop
- Line 198: Division operations that could use toolz

### infrastructure/message_repository.py (violations):
- Line 41: `for line_num, line in enumerate(f, 1)` - manual loop
- Line 49: `self._raw_messages.append(raw_msg)` - manual append
- Line 56: `messages.extend(message)` - manual extend
- Line 58: `messages.append(message)` - manual append
- Line 60: `self._errors.append((line_num, error_msg))` - manual append
- Line 96: `for message in messages` - manual loop
- Line 101: `for raw_msg in self._raw_messages` - manual loop

### Additional Violations Our Ruff Missed:
1. **Manual state tracking**: `count = 0; count += 1`
2. **Manual list building**: Creating empty list then appending
3. **Division for ratios**: Could use functional approach
4. **Set operations**: `session_ids = set()` then adding
5. **Break statements**: Imperative control flow
6. **Continue statements**: Imperative control flow
7. **Try-except in loops**: Should use functional error handling

## Fixes Using toolz/more-itertools

### Example Migration (parse_jsonl):

**BEFORE**:
```python
messages = []
errors = []
with open(filepath, 'rb') as f:
    for line_num, line in enumerate(f, 1):
        if not line.strip():
            continue
        try:
            data = orjson.loads(line)
            messages.append(data)
        except orjson.JSONDecodeError as e:
            errors.append((line_num, str(e)))
```

**AFTER**:
```python
from toolz import filter as toolz_filter, map as toolz_map, partition
from more_itertools import partition as more_partition

def parse_line_safe(indexed_line):
    """Parse a line, return (success, result) tuple."""
    line_num, line = indexed_line
    if not line.strip():
        return None
    try:
        return ('success', orjson.loads(line))
    except orjson.JSONDecodeError as e:
        logger.warning(f"Line {line_num}: Failed to parse JSON - {e}")
        return ('error', (line_num, str(e)))

with open(filepath, 'rb') as f:
    # Parse all lines functionally
    results = list(toolz_filter(
        lambda x: x is not None,
        toolz_map(parse_line_safe, enumerate(f, 1))
    ))
    
    # Partition into successes and errors
    errors_iter, successes_iter = more_partition(
        lambda x: x[0] == 'error', 
        results
    )
    
    messages = [item[1] for item in successes_iter]
    errors = [item[1] for item in errors_iter]
```

## New Ruff Rules to Add

```python
# Additional patterns to detect:
(r"count = \d+", "Use toolz.count or more_itertools.ilen"),
(r"\+= 1", "Use functional counting instead of increment"),
(r"\.add\(", "Use functional set operations"),
(r"\.update\(", "Use functional dict/set operations"),
(r"break(?:\s|$)", "Use takewhile or functional approach"),
(r"continue(?:\s|$)", "Use filter to skip items"),
(r"^\s*try:.*except.*for", "Use functional error handling"),
(r"= \[\]", "Don't initialize empty lists"),
(r"= \{\}", "Don't initialize empty dicts/sets"),
(r"if len\(", "Use more_itertools predicates"),
```

## Priority Order
1. Create new infrastructure files with functional code
2. Update imports
3. Run tests to ensure compatibility
4. Delete old parser.py
5. Update ruff detection rules
6. Fix remaining violations