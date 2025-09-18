# Claude Parser API Layering Audit

## Current State Analysis

### 🔴 Problems Identified

1. **Low-level utilities exposed as public API:**
   - `find_message_by_uuid` - Implementation detail
   - `restore_file_content`, `backup_file` - Too low-level
   - `compare_files`, `generate_file_diff` - Need context

2. **High-level utilities NOT exposed:**
   - `get_message_content()` - Needed for safe extraction
   - `filter_pure_conversation()` - Useful for UIs
   - `get_latest_assistant_message()` - Common UI need

3. **Mixed abstraction levels:**
   - Some domains expose everything (tokens)
   - Some expose nothing useful (messages)

## Proposed API Structure

### Core Layer (`claude_parser.core`)
Low-level building blocks for advanced users and library builders.

#### Core Messages
```python
from claude_parser.core.messages import (
    get_message_content,    # Safe content extraction
    get_text,              # Text from any message format
    get_token_usage,       # Extract usage metadata
    is_tool_operation,     # Check for tool use
)
```

#### Core Filtering
```python
from claude_parser.core.filtering import (
    filter_messages_by_type,
    filter_messages_by_tool,
    filter_pure_conversation,
    exclude_tool_operations,
)
```

#### Core Navigation
```python
from claude_parser.core.navigation import (
    find_message_by_uuid,
    get_message_sequence,
    find_current_checkpoint,
)
```

#### Core Storage
```python
from claude_parser.core.storage import (
    query_jsonl,           # Raw DuckDB access
    get_engine,           # Direct engine access
)
```

### Feature Layer (`claude_parser`)
High-level, UI-ready functions that use core internally.

#### Conversation Display
```python
from claude_parser import (
    get_conversation_for_display,  # Returns UI-ready messages
    get_conversation_summary,       # Quick stats
    format_message_for_ui,         # Single message formatting
)

# One-liner for UI:
messages = get_conversation_for_display(session)
# Returns: [
#   {'text': '...', 'role': 'user', 'timestamp': '...', 'has_tools': False},
#   {'text': '...', 'role': 'assistant', 'timestamp': '...', 'tools_used': ['Bash']}
# ]
```

#### File Operations Display
```python
from claude_parser import (
    get_file_changes_at_point,     # Get diff at specific message
    get_modified_files_list,        # List all changed files
    get_file_history,              # Timeline of file changes
)

# One-liner for diff UI:
changes = get_file_changes_at_point(session, uuid)
# Returns: {
#   'file': 'main.py',
#   'before': '...',
#   'after': '...',
#   'diff_html': '...',  # Pre-formatted for display
# }
```

#### Analytics Dashboard
```python
from claude_parser import (
    get_session_analytics,         # Complete dashboard data
    get_token_usage_summary,       # Token counts with costs
    get_tool_usage_report,         # Tool frequency analysis
)

# One-liner for dashboard:
analytics = get_session_analytics(session)
# Returns: {
#   'messages': {'total': 45, 'user': 20, 'assistant': 25},
#   'tokens': {'used': 6600, 'cost': 0.05, 'remaining': 193400},
#   'tools': {'Bash': 10, 'Write': 5},
#   'duration': '25 minutes'
# }
```

## Migration Plan

### Phase 1: Create Core Package
- Move internal functions to `claude_parser/core/`
- Keep backward compatibility with deprecation warnings

### Phase 2: Build Feature Layer
- Implement high-level functions using core
- Each feature function should be <20 LOC
- 100% framework delegation

### Phase 3: Update Public API
- Update `__init__.py` to expose both layers
- Documentation with clear examples
- Deprecate old mixed-level exports

## UI Projects Benefit

With this structure, UI projects like claude-explorer get:

```python
# Instead of this (current):
messages = session.get('messages', [])
filtered = filter_pure_conversation(messages)
formatted = []
for msg in filtered:
    content = msg.get('content', msg.get('message', {}).get('content', ''))
    if content:
        formatted.append({
            'text': content,
            'type': msg.get('type'),
            # ... more boilerplate
        })

# They get this (new):
messages = get_conversation_for_display(session)  # Done!
```

## Next Steps

1. ✅ Audit complete - we know what goes where
2. ⏳ Create `core/` package structure
3. ⏳ Implement feature layer functions
4. ⏳ Update documentation
5. ⏳ Release as v3.0.0 (breaking change)