# Parser Domain API

The Parser domain handles loading and parsing Claude Code JSONL conversation files.

## Quick Start (95% Use Case)

```python
from claude_parser import load

# One line to load everything
conv = load("session.jsonl")

# Instant access
print(f"📊 {len(conv)} messages")
print(f"🔧 {len(conv.tool_uses)} tool uses")
print(f"💬 {len(conv.user_messages)} user messages")
print(f"🤖 {len(conv.assistant_messages)} assistant messages")
```

---

## Core Functions

### `load(filepath, strict=False)`

Load a Claude conversation from JSONL file.

```python
from claude_parser import load

# Basic usage (95% case)
conv = load("session.jsonl")

# With validation (5% case)
conv = load("session.jsonl", strict=True)
```

**Parameters:**
- `filepath` (str | Path): Path to JSONL file
- `strict` (bool): Validate Claude format if True

**Returns:** `Conversation` object

**Raises:**
- `FileNotFoundError`: File doesn't exist
- `ValueError`: Invalid JSONL or format

### `load_many(filepaths)`

Load multiple conversations at once.

```python
from claude_parser import load_many

convs = load_many(["session1.jsonl", "session2.jsonl"])
total = sum(len(c) for c in convs)
```

---

## Conversation Class

The main aggregate root for the Parser domain.

```python
class Conversation:
    """A Claude conversation from JSONL."""
    
    # Properties
    messages: List[Message]           # All messages
    session_id: Optional[str]         # Session identifier
    user_messages: List[UserMessage]  # User messages only
    assistant_messages: List[AssistantMessage]  # Assistant only
    tool_uses: List[ToolUse | ToolResult]  # Tools
    summaries: List[Summary]          # Summaries
    current_dir: Optional[str]        # Working directory
    git_branch: Optional[str]         # Git branch
    errors: List[tuple[int, str]]     # Parse errors
    
    # Core methods
    def search(text, case_sensitive=False) -> List[Message]
    def filter(predicate) -> List[Message]
    def with_errors() -> List[Message]
    def messages_messages_before_summary(limit=20) -> List[Message]
```

### Search Methods

```python
# Find messages containing text
python_msgs = conv.search("python")
errors = conv.search("error")

# Case-sensitive search
exact = conv.search("Python", case_sensitive=True)

# Find error messages
error_msgs = conv.with_errors()

# Custom filters
long_msgs = conv.filter(lambda m: len(m.text_content) > 1000)
```

### Navigation

```python
# Access by index
first = conv[0]
last = conv[-1]
subset = conv[10:20]

# Iteration
for msg in conv:
    print(f"{msg.type}: {msg.text_content[:50]}")

# Get context before summary
recent = conv.before_summary(10)
```

---

## Advanced API (5% Use Cases)

### Streaming Parser

For large files or memory-constrained environments:

```python
from claude_parser.parser import parse_jsonl_streaming

# Process one message at a time
for msg_dict in parse_jsonl_streaming("huge.jsonl"):
    if msg_dict.get("type") == "tool_use":
        process_tool(msg_dict)
```

### Validation Functions

```python
from claude_parser.parser import (
    validate_jsonl,
    validate_claude_format,
    count_messages
)

# Check file validity
is_valid, errors = validate_jsonl("file.jsonl")
is_claude, issues = validate_claude_format("file.jsonl")

# Count without loading
count = count_messages("file.jsonl")
```

---

## Examples

### Tool Usage Analysis

```python
conv = load("session.jsonl")

# Count tool usage
from collections import Counter
tool_counts = Counter()

for tool in conv.tool_uses:
    if hasattr(tool, 'tool_name'):
        tool_counts[tool.tool_name] += 1

print("Top tools:", tool_counts.most_common(5))
```

### Error Debugging

```python
conv = load("debug_session.jsonl")

# Find errors
errors = conv.with_errors()
print(f"Found {len(errors)} errors")

# Search for specific error patterns
timeout_msgs = conv.search("timeout")
failed_msgs = conv.search("failed")
```

### Extract Learnings

```python
def extract_insights(conv):
    insights = []
    
    # Get summaries
    for summary in conv.summaries:
        insights.append({
            "type": "summary",
            "content": summary.text_content
        })
    
    # Get successful patterns
    for tool in conv.tool_uses:
        if tool.tool_name == "Write":
            insights.append({
                "type": "file_created",
                "params": tool.parameters
            })
    
    return insights
```

---

## Performance

- **Loading**: ~3,000 messages in 0.1-0.2 seconds
- **Memory**: ~4x file size (10MB file → 40MB RAM)
- **Search**: Linear scan, ~1M messages/second
- **Streaming**: Constant memory usage

---

## See Also

- [Models](./models.md) - Message types and structures
- [Error Handling](./errors.md) - Handling parse errors
- [Performance](./performance.md) - Optimization tips