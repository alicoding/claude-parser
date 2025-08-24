# Navigation Libraries Research (95/5 Principle)

## Current Violations - Custom Code We Wrote

### 1. UUID Index for O(1) Lookup
```python
# VIOLATION: Custom hashmap
self._uuid_index = {msg.uuid: msg for msg in messages}
```
**Need**: Library for fast key-value lookups with large datasets

### 2. Thread Navigation 
```python
# VIOLATION: Custom parent-child traversal
def get_thread_from(self, uuid: str):
    children_map = {}
    for msg in self._messages:
        if msg.parent_uuid:
            children_map[msg.parent_uuid].append(msg)
```
**Need**: Graph/tree traversal library (NetworkX? anytree?)

### 3. Timestamp Range Queries
```python
# VIOLATION: Custom filtering
return [msg for msg in self._messages 
        if start <= msg.timestamp <= end]
```
**Need**: Time-series or indexed query library (pandas? bisect?)

### 4. Message Filtering
```python
# VIOLATION: List comprehensions everywhere
return [msg for msg in self._messages if condition]
```
**Need**: Query/filter library (pandas? SQLite in-memory?)

## Potential Battle-Tested Solutions

### Option 1: pandas DataFrame
- ✅ Built-in indexing for O(1) UUID lookup
- ✅ Timestamp filtering with DatetimeIndex
- ✅ Powerful query/filter operations
- ✅ groupby for session/type filtering
- ❌ Overkill for simple navigation?

### Option 2: NetworkX for Threading
- ✅ Graph algorithms for parent-child relationships
- ✅ Built-in tree traversal
- ✅ Branch detection and path finding
- ✅ Well-tested and maintained

### Option 3: SQLite In-Memory
- ✅ SQL queries for complex filtering
- ✅ Indexes for O(1) lookups
- ✅ Window functions for surrounding context
- ✅ Built into Python stdlib

### Option 4: Keep It Simple
- Use `bisect` for timestamp ranges (stdlib)
- Use `dict` for UUID index (already doing this)
- Use NetworkX only for thread navigation
- Avoid over-engineering

## Questions for Research Tool

1. Is pandas appropriate for conversation navigation or overkill?
2. What's the best graph library for message threading (NetworkX vs igraph vs anytree)?
3. Should we use SQLite in-memory for all navigation queries?
4. Are there specialized conversation/chat libraries we're missing?
5. What do other JSONL parsers use for navigation?

## 95/5 Principle Reminder

The 95% use case is:
- Find message by UUID
- Get surrounding context
- Filter by type
- Search by text

We should optimize for these, not complex graph traversal.