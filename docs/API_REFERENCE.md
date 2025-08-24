# Claude Parser SDK - API Reference

## Overview

Claude Parser SDK is a Python library for parsing and analyzing Claude Code conversation exports (JSONL files). It follows the **95/5 principle** - 95% of users need just one line of code, while 5% get full power through the complete API.

## Quick Start (95% Use Case)

```python
from claude_parser import load

# Load any Claude Code export
conv = load("session.jsonl")

# Instant access to everything
print(f"📊 {len(conv)} messages")
print(f"🔧 {len(conv.tool_uses)} tool uses") 
print(f"💬 {len(conv.user_messages)} user messages")
print(f"🤖 {len(conv.assistant_messages)} assistant messages")

# Search across all content
results = conv.search("python")
print(f"🔍 Found 'python' in {len(results)} messages")
```

---

## Core API

### Main Functions

#### `load(filepath, strict=False)`

**The 95% use case** - Load a Claude conversation from JSONL file.

```python
from claude_parser import load

# Basic usage (recommended)
conv = load("session.jsonl")

# Strict validation (optional)
conv = load("session.jsonl", strict=True)  # Validates Claude format
```

**Parameters:**
- `filepath` (str | Path): Path to Claude Code JSONL export file
- `strict` (bool): If True, validates file follows Claude Code format

**Returns:** `Conversation` object

**Raises:**
- `FileNotFoundError`: If JSONL file doesn't exist
- `ValueError`: If file is invalid JSONL or (strict=True) not Claude format

---

#### `load_many(filepaths)`

Load multiple conversations at once.

```python
from claude_parser import load_many

convs = load_many(["session1.jsonl", "session2.jsonl", "session3.jsonl"])
total_messages = sum(len(c) for c in convs)
```

**Parameters:**
- `filepaths` (List[str | Path]): List of paths to JSONL files

**Returns:** `List[Conversation]`

---

### Conversation Class

The main interface for working with Claude conversations.

```python
class Conversation:
    """Represents a Claude conversation from JSONL file."""
    
    # Properties
    messages: List[Message]           # All messages
    session_id: Optional[str]         # Session ID if available
    user_messages: List[UserMessage] # Only user messages
    assistant_messages: List[AssistantMessage] # Only assistant messages
    tool_uses: List[ToolUse | ToolResult] # All tool uses/results
    summaries: List[Summary]          # All summary messages
    current_dir: Optional[str]        # Working directory
    git_branch: Optional[str]         # Git branch if available
    errors: List[tuple[int, str]]     # Parsing errors
    
    # Methods
    def search(text, case_sensitive=False) -> List[Message]
    def filter_messages(predicate) -> List[Message]
    def messages_messages_before_summary(limit=20) -> List[Message]
    def messages_with_errors() -> List[Message]
    
    # Iteration support
    def __len__() -> int
    def __getitem__(index) -> Message | List[Message]
    def __iter__() -> Iterator[Message]
```

---

## Properties Reference

### Basic Properties

```python
conv = load("session.jsonl")

# Message counts
print(f"Total messages: {len(conv)}")
print(f"User messages: {len(conv.user_messages)}")
print(f"Assistant messages: {len(conv.assistant_messages)}")
print(f"Tool uses/results: {len(conv.tool_uses)}")
print(f"Summaries: {len(conv.summaries)}")

# Session metadata
print(f"Session ID: {conv.session_id}")
print(f"Working directory: {conv.current_dir}")
print(f"Git branch: {conv.git_branch}")

# Quality check
if conv.errors:
    print(f"⚠️ {len(conv.errors)} parsing errors")
```

### Message Types

Each message type has specific properties:

```python
# User messages
for msg in conv.user_messages:
    print(f"User: {msg.text_content}")
    print(f"Timestamp: {msg.timestamp}")

# Assistant messages  
for msg in conv.assistant_messages:
    print(f"Assistant: {msg.text_content}")
    print(f"Model: {msg.message.get('model', 'unknown')}")

# Tool uses
for tool in conv.tool_uses:
    if isinstance(tool, ToolUse):
        print(f"🔧 {tool.tool_name}: {tool.parameters}")
    elif isinstance(tool, ToolResult):
        print(f"📄 Result: {tool.result_text[:100]}...")

# Summaries
for summary in conv.summaries:
    print(f"📝 {summary.text_content}")
```

---

## Methods Reference

### Search Methods

#### `search(text, case_sensitive=False)`

Search for messages containing text across all message types.

```python
# Case-insensitive search (default)
python_msgs = conv.search("python")
error_msgs = conv.search("error")

# Case-sensitive search
exact_msgs = conv.search("Python", case_sensitive=True)

# Search works across all content types:
# - User message text
# - Assistant message text  
# - Tool parameters and results
# - Summary content
# - System message content
```

#### `with_errors()`

Find messages that likely contain errors.

```python
error_msgs = conv.with_errors()
for msg in error_msgs:
    print(f"❌ {msg.type}: {msg.text_content[:100]}...")
```

#### `filter(predicate)`

Filter messages with custom logic.

```python
# Messages from today
from datetime import datetime
today_msgs = conv.filter(
    lambda msg: msg.timestamp and 
    msg.timestamp.startswith(datetime.now().strftime("%Y-%m-%d"))
)

# Long messages
long_msgs = conv.filter(
    lambda msg: len(msg.text_content) > 1000
)

# Tool uses only
tools_only = conv.filter(
    lambda msg: msg.type in [MessageType.TOOL_USE, MessageType.TOOL_RESULT]
)
```

### Navigation Methods

#### `before_summary(limit=20)`

Get messages before the last summary (useful for context).

```python
# Get last 10 messages before summary
recent = conv.before_summary(10)
for msg in recent:
    print(f"{msg.type}: {msg.text_content[:50]}...")
```

### Iteration Support

```python
conv = load("session.jsonl")

# Length
print(f"Messages: {len(conv)}")

# Indexing
first_msg = conv[0]
last_msg = conv[-1]
middle_msgs = conv[10:20]

# Iteration
for msg in conv:
    print(f"{msg.type}: {msg.text_content[:50]}...")
    
# Enumerate
for i, msg in enumerate(conv):
    print(f"{i}: {msg.type}")
```

---

## Message Types Reference

### MessageType Enum

```python
from claude_parser import MessageType

MessageType.USER        # "user" 
MessageType.ASSISTANT   # "assistant"
MessageType.TOOL_USE    # "tool_use"
MessageType.TOOL_RESULT # "tool_result" 
MessageType.SUMMARY     # "summary"
MessageType.SYSTEM      # "system"
```

### Message Models

All messages inherit from `BaseMessage`:

```python
class BaseMessage:
    type: MessageType
    timestamp: Optional[str]
    uuid: Optional[str] 
    session_id: Optional[str]
    parent_uuid: Optional[str]
    
    @property
    def parsed_timestamp(self) -> Optional[DateTime]:
        """Parse timestamp to pendulum DateTime."""
```

#### UserMessage

```python
class UserMessage(BaseMessage):
    type: MessageType = MessageType.USER
    message: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    
    @property
    def text_content(self) -> str:
        """Extract readable text from user message."""
```

#### AssistantMessage  

```python
class AssistantMessage(BaseMessage):
    type: MessageType = MessageType.ASSISTANT
    message: Optional[Dict[str, Any]] = None
    content: Optional[str] = None
    
    @property  
    def text_content(self) -> str:
        """Extract readable text from assistant message."""
```

#### ToolUse

```python
class ToolUse(BaseMessage):
    type: MessageType = MessageType.TOOL_USE
    tool_use_id: Optional[str] = None
    name: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    
    @property
    def tool_name(self) -> str:
        """Get tool name."""
        
    @property
    def text_content(self) -> str:
        """Searchable text combining tool name and parameters."""
```

#### ToolResult

```python
class ToolResult(BaseMessage):
    type: MessageType = MessageType.TOOL_RESULT
    tool_use_id: Optional[str] = None
    tool_use_result: Optional[str] = None
    
    @property
    def result_text(self) -> str:
        """Get tool execution result."""
        
    @property
    def text_content(self) -> str:
        """Searchable text content."""
```

#### Summary

```python
class Summary(BaseMessage):
    type: MessageType = MessageType.SUMMARY
    summary: Optional[str] = None
    leaf_uuid: Optional[str] = None
    
    @property
    def text_content(self) -> str:
        """Get summary text."""
```

#### SystemMessage

```python
class SystemMessage(BaseMessage):
    type: MessageType = MessageType.SYSTEM
    content: Optional[str] = None
    
    @property
    def text_content(self) -> str:
        """Get system message text."""
```

---

## Advanced API (5% Use Cases)

### Direct Parser Functions

For advanced use cases requiring more control:

```python
from claude_parser.parser import (
    parse_jsonl,           # Parse entire file to list
    parse_jsonl_streaming, # Memory-efficient streaming
    count_messages,        # Count without loading
    validate_jsonl,        # Validate JSONL format
    validate_claude_format # Validate Claude format
)

# Streaming for large files (memory efficient)
for message_dict in parse_jsonl_streaming("large_file.jsonl"):
    # Process one message at a time
    if message_dict.get("type") == "tool_use":
        print(f"Tool: {message_dict.get('name')}")

# Count messages without loading
msg_count = count_messages("session.jsonl")
print(f"File contains {msg_count} messages")

# Validation
is_valid_jsonl, error_lines = validate_jsonl("file.jsonl")
is_claude_format, errors = validate_claude_format("file.jsonl")
```

### Direct Model Creation

```python
from claude_parser.models import parse_message

# Parse individual message
raw_msg = {"type": "user", "content": "Hello"}
msg = parse_message(raw_msg)
```

---

## Error Handling

### Common Exceptions

```python
from claude_parser import load

try:
    conv = load("nonexistent.jsonl")
except FileNotFoundError:
    print("❌ File not found")

try:
    conv = load("invalid.jsonl", strict=True)
except ValueError as e:
    print(f"❌ Validation error: {e}")
```

### Parsing Errors

```python
conv = load("partially_corrupted.jsonl")

# Check for parsing issues
if conv.errors:
    print(f"⚠️ {len(conv.errors)} messages failed to parse:")
    for line_num, error in conv.errors:
        print(f"  Line {line_num}: {error}")

# Still get successfully parsed messages
print(f"✅ {len(conv)} messages parsed successfully")
```

---

## Real-World Examples

### 1. Debugging Session Analysis

```python
from claude_parser import load

# Load debugging session
conv = load("debug_session.jsonl")

# Find all error messages
errors = conv.with_errors()
print(f"🐛 Found {len(errors)} error messages")

# Get tool usage statistics
tools = conv.tool_uses
tool_counts = {}
for tool in tools:
    if hasattr(tool, 'tool_name'):
        name = tool.tool_name
        tool_counts[name] = tool_counts.get(name, 0) + 1

print("🔧 Tool usage:")
for tool, count in sorted(tool_counts.items()):
    print(f"  {tool}: {count} uses")
```

### 2. Code Review Analysis

```python
# Find all code-related discussions
code_terms = ["function", "class", "import", "def", "async", "await"]
code_messages = []

for term in code_terms:
    matches = conv.search(term, case_sensitive=False)
    code_messages.extend(matches)

# Remove duplicates
unique_code_msgs = list({msg.uuid: msg for msg in code_messages if msg.uuid}.values())
print(f"💻 {len(unique_code_msgs)} code-related messages")
```

### 3. Memory Integration Example

```python
from claude_parser import load
# from mem0 import MemoryClient  # Your memory system

def extract_learnings(conv):
    """Extract key learnings for memory storage."""
    learnings = []
    
    # Get summaries (high-level insights)
    for summary in conv.summaries:
        learnings.append({
            "type": "summary",
            "content": summary.text_content,
            "timestamp": summary.timestamp
        })
    
    # Get successful tool patterns
    for tool in conv.tool_uses:
        if hasattr(tool, 'tool_name') and tool.tool_name:
            learnings.append({
                "type": "tool_pattern", 
                "tool": tool.tool_name,
                "params": tool.parameters,
                "timestamp": tool.timestamp
            })
    
    return learnings

# Process conversation
conv = load("session.jsonl")
insights = extract_learnings(conv)
print(f"🧠 Extracted {len(insights)} learnings")
```

### 4. Analytics Dashboard Data

```python
from collections import Counter
from datetime import datetime

def analyze_conversation(conv):
    """Generate analytics for dashboard."""
    
    # Message timeline
    timeline = []
    for msg in conv.messages:
        if msg.timestamp:
            timeline.append({
                "timestamp": msg.timestamp,
                "type": msg.type.value,
                "length": len(msg.text_content)
            })
    
    # Tool usage patterns
    tool_usage = Counter()
    for tool in conv.tool_uses:
        if hasattr(tool, 'tool_name'):
            tool_usage[tool.tool_name] += 1
    
    # Error frequency
    error_msgs = conv.with_errors()
    
    return {
        "total_messages": len(conv),
        "session_duration": timeline[-1]["timestamp"] if timeline else None,
        "top_tools": dict(tool_usage.most_common(5)),
        "error_rate": len(error_msgs) / len(conv) if conv else 0,
        "timeline": timeline
    }

# Generate dashboard data
stats = analyze_conversation(conv)
print(f"📊 Analytics: {stats}")
```

---

## Performance Notes

### Memory Efficiency

```python
# For large files, use streaming
from claude_parser.parser import parse_jsonl_streaming

# Memory efficient - one message at a time
for msg_dict in parse_jsonl_streaming("large_file.jsonl"):
    # Process immediately, don't store all
    process_message(msg_dict)

# vs loading all at once (uses more memory)
conv = load("large_file.jsonl")  # Loads everything
```

### Performance Benchmarks

- **Loading**: ~3,000 messages in 0.1-0.2 seconds
- **Memory**: ~4x file size (e.g., 10MB file → 40MB RAM)
- **Search**: Linear scan, ~1M messages/second
- **Tool extraction**: Handles embedded tool format efficiently

---

## Library Dependencies

Following strict **Library-First** principle:

- **orjson**: 10x faster JSON parsing (vs standard json)
- **pydantic v2**: 10x faster type validation  
- **pendulum**: Better datetime handling
- **loguru**: Modern logging
- **pathlib**: Proper path handling

**No custom low-level components** - everything uses best-in-class libraries.

---

## Version Compatibility

- **Python**: 3.10+
- **Claude Code**: All export formats (2024-2025)
- **Pydantic**: v2.0+
- **Type hints**: Full support

---

## Support

For issues, feature requests, or questions:
- GitHub Issues: [claude-parser/issues](https://github.com/your-org/claude-parser/issues)
- Documentation: [claude-parser docs](https://docs.your-org.com/claude-parser)

---

## License

MIT License - see LICENSE file for details.