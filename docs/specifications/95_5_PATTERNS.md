# 95/5 Pattern Replacements Guide

## 🎯 The Goal: Use toolz/more-itertools for EVERYTHING

### ❌ BANNED → ✅ REPLACEMENT

## List Operations

### ❌ Empty list + append
```python
# BANNED
result = []
for item in items:
    result.append(process(item))
```

### ✅ Use toolz.map
```python
from toolz import map as toolz_map
result = list(toolz_map(process, items))
```

---

## List Building with Conditions

### ❌ Empty list + conditional append
```python
# BANNED
errors = []
if condition1:
    errors.append("error1")
if condition2:
    errors.append("error2")
```

### ✅ Use toolz.concat with filter
```python
from toolz import concat, filter as toolz_filter

def check_conditions(data):
    """Return list of errors or empty list"""
    checks = [
        ("error1" if condition1 else None),
        ("error2" if condition2 else None),
    ]
    return list(toolz_filter(None, checks))
```

---

## For Loops with Enumerate

### ❌ Manual enumeration
```python
# BANNED
for i, line in enumerate(lines, 1):
    if line.strip():
        process(i, line)
```

### ✅ Use toolz with enumerate
```python
from toolz import pipe, filter as toolz_filter, map as toolz_map

result = pipe(
    enumerate(lines, 1),
    toolz_filter(lambda x: x[1].strip()),
    toolz_map(lambda x: process(x[0], x[1])),
    list
)
```

---

## List Comprehensions

### ❌ List comprehension
```python
# BANNED
result = [x * 2 for x in items if x > 0]
```

### ✅ Use toolz.pipe
```python
from toolz import pipe, filter as toolz_filter, map as toolz_map

result = pipe(
    items,
    toolz_filter(lambda x: x > 0),
    toolz_map(lambda x: x * 2),
    list
)
```

---

## Error Collection

### ❌ Manual error collection
```python
# BANNED
errors = []
for item in items:
    try:
        process(item)
    except Exception as e:
        errors.append(str(e))
```

### ✅ Use toolz.excepts
```python
from toolz import excepts, map as toolz_map

def safe_process(item):
    return excepts(Exception, process, lambda e: f"Error: {e}")(item)

results = list(toolz_map(safe_process, items))
errors = [r for r in results if r.startswith("Error:")]
```

---

## Continue/Break Patterns

### ❌ Continue in loop
```python
# BANNED
for item in items:
    if not item:
        continue
    process(item)
```

### ✅ Use toolz.filter
```python
from toolz import pipe, filter as toolz_filter, map as toolz_map

pipe(
    items,
    toolz_filter(bool),  # Skip falsy items
    toolz_map(process),
    list
)
```

---

## State Management

### ❌ Manual state tracking
```python
# BANNED
count = 0
for item in items:
    if condition(item):
        count += 1
```

### ✅ Use toolz.count
```python
from toolz import count, filter as toolz_filter

result = count(toolz_filter(condition, items))
```

---

## Complex Pipeline Example

### ❌ Multiple operations with state
```python
# BANNED
messages = []
errors = []
for line_num, line in enumerate(file, 1):
    if not line.strip():
        continue
    try:
        msg = parse(line)
        messages.append(msg)
    except Exception as e:
        errors.append((line_num, str(e)))
```

### ✅ Functional pipeline
```python
from toolz import pipe, filter as toolz_filter, map as toolz_map, partition

def parse_with_line_num(indexed_line):
    line_num, line = indexed_line
    try:
        return ('success', parse(line))
    except Exception as e:
        return ('error', (line_num, str(e)))

results = pipe(
    enumerate(file, 1),
    toolz_filter(lambda x: x[1].strip()),  # Skip empty lines
    toolz_map(parse_with_line_num),
    list
)

# Partition results
successes, errors = partition(lambda x: x[0] == 'error', results)
messages = [msg for _, msg in successes]
error_list = [err for _, err in errors]
```

---

## Key Principles

1. **NEVER** initialize empty lists/dicts
2. **NEVER** use append/extend
3. **ALWAYS** use pipe for multiple operations
4. **ALWAYS** use toolz_map instead of list comprehensions
5. **ALWAYS** use toolz_filter instead of if/continue
6. **PREFER** immutable operations over state mutation

## Available Functions from toolz

- `map` - Transform items
- `filter` - Select items  
- `reduce` - Aggregate items
- `pipe` - Chain operations
- `compose` - Create function pipelines
- `concat` - Flatten lists
- `mapcat` - Map then concat
- `partition` - Split by predicate
- `groupby` - Group by key
- `count` - Count items
- `take` - Take first n
- `drop` - Skip first n
- `unique` - Remove duplicates
- `merge` - Merge dicts
- `excepts` - Exception handling

## Remember

**The 95/5 Principle**: Your code should be 95% library calls, 5% business logic.
If you're writing loops, you're doing it wrong!