# Timeline Domain

Git-like functionality for JSONL recovery and navigation.

## Implementation

- **File**: `claude_parser/timeline.py` (113 lines)
- **Tests**: `tests/test_timeline.py`

## Architecture

### 95/5 Principle Compliance
- 95% library code, 5% glue
- 10 library imports, minimal custom logic

### Libraries Used
1. **GitPython** - Complete git operations (branches, commits, checkout, merge)
2. **jsonlines** - JSONL parsing (not json)
3. **jmespath** - Query operations
4. **deepdiff** - State comparison
5. **pathlib** - File operations
6. **more_itertools** - Collection operations
7. **functools** - LRU caching
8. **tempfile** - Temporary directories

## Features

### Core Operations
- `checkout(point)` - Checkout any point in time
- `branch(name)` - Create branches
- `merge(branch, into)` - Merge branches
- `diff(from_point, to_point)` - Compare states
- `query(expression, limit)` - Query commits with JMESPath

### Event Support
- Write operations
- Edit operations
- MultiEdit operations

## Usage

```python
from claude_parser.timeline import Timeline

# Initialize with JSONL directory
timeline = Timeline(Path("/path/to/jsonl"))

# Checkout latest state
state = timeline.checkout("latest")

# Create branch
timeline.branch("recovery-point")

# Query commits
commits = timeline.query("[?contains(message, 'important')]")

# Diff between points
changes = timeline.diff("branch:v1", "branch:v2")

# Cleanup when done
timeline.clear_cache()
```

## Design Decisions

1. **Git as backend**: Instead of implementing versioning, we use Git
2. **Temporary repos**: Each Timeline instance creates a temp git repo
3. **Event replay**: Events become git commits for full history
4. **Library delegation**: Every operation delegates to a library
5. **Auto cleanup**: Temp directories cleaned on `clear_cache()`

## Performance

- LRU cache for repeated checkouts
- Streaming JSONL parsing
- Git's efficient storage and operations
- Temporary filesystem for isolation