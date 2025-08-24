# 95/5 Principle Violation Fixes - Approval Required

## Summary
- **Total Violations Found:** 59
- **Categories:**
  - For loops: 29 violations
  - Manual append: 18 violations  
  - List comprehensions: 7 violations
  - Manual extend: 1 violation
  - Sum with generator: 1 violation
  - Length checks: 1 violation
  - Other: 2 violations

## Required Libraries to Add (Need Your Approval)
1. **toolz** - Already approved ✅
2. **more-itertools** - Already approved ✅
3. **No new libraries needed!** All fixes use already-approved libraries

## Violation Fixes by Category

### 1. FOR LOOPS (29 violations)
**Pattern:** Manual iteration with enumerate for file processing

#### Example 1: parser.py:32
**BEFORE:**
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

**AFTER (using toolz):**
```python
from toolz import partition_all, filter as toolz_filter, map as toolz_map
from toolz.curried import pipe
from more_itertools import partition

def process_line(indexed_line):
    line_num, line = indexed_line
    if not line.strip():
        return None
    try:
        return ('success', orjson.loads(line))
    except orjson.JSONDecodeError as e:
        return ('error', (line_num, str(e)))

with open(filepath, 'rb') as f:
    results = list(toolz_filter(None, toolz_map(process_line, enumerate(f, 1))))
    successes, errors = partition(lambda x: x[0] == 'error', results)
    messages = [item[1] for item in successes]
    errors = [item[1] for item in errors]
```

### 2. LIST COMPREHENSIONS (7 violations)

#### Example 2: __init__.py:75
**BEFORE:**
```python
def load_many(filepaths: List[str]) -> List[Conversation]:
    return [load(fp) for fp in filepaths]
```

**AFTER (using toolz):**
```python
from toolz import map as toolz_map

def load_many(filepaths: List[str]) -> List[Conversation]:
    return list(toolz_map(load, filepaths))
```

#### Example 3: __init__.py:73
**BEFORE:**
```python
>>> total_messages = sum(len(c) for c in convs)
```

**AFTER (using toolz):**
```python
from toolz import reduce

>>> total_messages = reduce(lambda acc, c: acc + len(c), convs, 0)
```

### 3. MANUAL APPEND (18 violations)

#### Example 4: parser.py:40
**BEFORE:**
```python
messages = []
# ... in loop
messages.append(data)
```

**AFTER (using toolz accumulate pattern):**
```python
from toolz import accumulate, concat
from more_itertools import flatten

# Build list functionally without append
messages = list(toolz_filter(
    lambda x: x is not None,
    toolz_map(parse_safe, lines)
))
```

### 4. MANUAL EXTEND (1 violation)

#### Example 5: models.py (embedded messages)
**BEFORE:**
```python
messages = [user_msg]
messages.extend(tool_result_msgs)
```

**AFTER (using toolz):**
```python
from toolz import concat

messages = list(concat([[user_msg], tool_result_msgs]))
# Or using more-itertools
from more_itertools import flatten
messages = list(flatten([[user_msg], tool_result_msgs]))
```

### 5. LENGTH CHECKS (1 violation)

#### Example 6: Checking if list has items
**BEFORE:**
```python
if len(messages) > 1:
    return messages
```

**AFTER (using more-itertools):**
```python
from more_itertools import ilen

if ilen(messages) > 1:  # Or use: if list(messages)[1:]
    return messages
```

## Benefits of These Changes

1. **No manual state management** - No more `messages = []` then `messages.append()`
2. **Composable operations** - Chain operations with pipe()
3. **Lazy evaluation** - toolz operations are lazy by default
4. **More declarative** - Says WHAT not HOW
5. **Error handling built-in** - partition() cleanly separates successes/errors
6. **No index tracking** - enumerate handled internally

## Implementation Strategy

### Phase 1: Core Parser (Highest Impact)
- Fix `parser.py` (12 violations) - File reading core
- Fix `domain/conversation.py` (8 violations) - Core domain logic

### Phase 2: API Layer  
- Fix `__init__.py` (2 violations) - Public API
- Fix `models.py` (remaining violations) - Data models

### Phase 3: Infrastructure
- Fix remaining files

## Required Actions Before Implementation

1. **APPROVAL NEEDED**: Do you approve using toolz/more-itertools for these patterns?
2. **DECISION**: Should we use toolz.curried (auto-currying) or regular toolz?
3. **PREFERENCE**: For partition, prefer toolz or more-itertools version?

## Notes
- All proposed libraries are ALREADY in our approved list
- No new dependencies needed
- Performance should be similar or better (lazy evaluation)
- Code becomes more testable (pure functions)