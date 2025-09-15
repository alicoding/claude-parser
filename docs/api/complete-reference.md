# Complete API Reference - All Domains

## Overview
Claude Parser exposes APIs across 15 domains. This reference covers ALL public functions.

## Core Public API (from `__init__.py`)

These are the main exports available when you `import claude_parser`:

### Session Management
- `load_session(jsonl_path: str) -> Dict` - Load a single session
- `load_latest_session() -> Dict` - Load most recent session
- `discover_all_sessions() -> List[Path]` - Find all sessions
- `load_many(*paths) -> List[Dict]` - Load multiple sessions
- `find_current_transcript() -> Dict` - Alias for load_latest_session
- `SessionManager` - Class for session management

### Analytics
- `analyze_session(session: Dict) -> Dict` - Analyze session statistics
- `analyze_project_contexts(session: Dict) -> Dict` - Analyze project contexts
- `analyze_tool_usage(session: Dict) -> Dict` - Analyze tool usage patterns

### Discovery
- `discover_claude_files() -> List[Path]` - Find all Claude files
- `discover_current_project_files() -> List[Path]` - Find project files
- `group_by_projects(files: List[Path]) -> Dict` - Group by projects
- `analyze_project_structure(project_path: str) -> Dict` - Analyze structure

### Operations
- `restore_file_content(file_path: str, session: Dict) -> str` - Restore file
- `generate_file_diff(file_path: str, session: Dict) -> str` - Generate diff
- `compare_files(file1: str, file2: str) -> str` - Compare two files
- `backup_file(file_path: str) -> str` - Create backup

### Navigation
- `find_message_by_uuid(uuid: str, session: Dict) -> Dict` - Find by UUID
- `get_message_sequence(start: str, end: str, session: Dict) -> List` - Get sequence
- `get_timeline_summary(session: Dict) -> Dict` - Timeline summary

### Tokens
- `count_tokens(text: str) -> int` - Count tokens
- `analyze_token_usage(session: Dict) -> Dict` - Token analysis
- `estimate_cost(total_tokens: int, model: str = None) -> float` - Estimate cost
- `token_status(session: Dict) -> Dict` - Token status
- `calculate_context_window(jsonl_path: str = None) -> Dict` - Context window
- `calculate_session_cost(input_tokens: int, output_tokens: int, ...) -> Dict` - Session cost

### Constants
- `MessageType.USER` - User message type constant
- `MessageType.ASSISTANT` - Assistant message type constant
- `MessageType.SYSTEM` - System message type constant
- `__version__` - Package version ("2.0.0")

## Domain-Specific APIs

### 1. Analytics Domain (`analytics/`)

```python
from claude_parser.analytics import *
```

**Core Functions:**
- Session analysis and statistics
- Tool usage tracking
- Project context analysis
- Cost calculations

### 2. CLI Domain (`cli/`)

**CG Commands** (`cg.py`, `cg_*.py`):
- Git-like interface for session navigation
- See [CLI Commands Documentation](../cli/commands.md)

**CH Command** (`ch.py`):
- Composable hook runner
- Pluggable executor system

### 3. Discovery Domain (`discovery/`)

```python
from claude_parser.discovery import *
```

**Functions:**
- `discover_claude_files()` - Find all Claude files on system
- `discover_current_project_files()` - Current project files
- `group_by_projects(files)` - Group files by project
- `analyze_project_structure(path)` - Analyze project

### 4. Filtering Domain (`filtering/`)

```python
from claude_parser.filtering import (
    filter_messages_by_type,
    filter_messages_by_tool,
    search_messages_by_content,
    filter_hook_events_by_type,
    filter_pure_conversation,
    exclude_tool_operations
)
```

**Message Filtering:**
- `filter_messages_by_type(messages, msg_type)` - Filter by type
- `filter_messages_by_tool(messages, tool_name)` - Filter by tool
- `search_messages_by_content(messages, pattern)` - Content search
- `filter_hook_events_by_type(messages, event_type)` - Hook events
- `filter_pure_conversation(messages)` - Conversation only
- `exclude_tool_operations(messages)` - No tool messages

### 5. Hooks Domain (`hooks/`)

```python
from claude_parser.hooks.api import (
    parse_hook_input,
    allow_operation,
    block_operation,
    request_approval,
    add_context,
    execute_hook
)
```

**Hook API Functions:**
- `parse_hook_input() -> Dict` - Parse stdin hook data
- `allow_operation(reason: str = "")` - Allow operation
- `block_operation(reason: str)` - Block operation
- `request_approval(reason: str)` - Request user approval
- `add_context(text: str)` - Add context for Claude
- `execute_hook(plugin_callback: Callable)` - Execute with callback

**Hook Handlers** (`handlers.py`):
- `handle_pre_tool_use(tool_name, tool_input)` - Pre-tool validation
- `handle_post_tool_use(tool_name, tool_response)` - Post-tool analysis
- `handle_user_prompt(prompt)` - User prompt filtering
- `handle_notification(message)` - Notifications
- `route_hook_event(hook_event_name, **kwargs)` - Event routing

### 6. Loaders Domain (`loaders/`)

```python
from claude_parser.loaders.session import load_session
from claude_parser.loaders.discovery import discover_all_sessions
```

**Loading Functions:**
- Session loading with JSON parsing
- File discovery with pathlib

### 7. Messages Domain (`messages/`)

Message processing utilities (check `messages/__init__.py` for exports)

### 8. Models Domain (`models/`)

Data models and utilities (check `models/__init__.py` for exports)

### 9. Navigation Domain (`navigation/`)

```python
from claude_parser.navigation import *
```

**Navigation Functions:**
- `find_message_by_uuid(uuid, session)` - UUID lookup
- `get_message_sequence(start, end, session)` - Message range
- `get_timeline_summary(session)` - Timeline overview
- Checkpoint detection for recovery points

### 10. Operations Domain (`operations/`)

```python
from claude_parser.operations import *
```

**File Operations:**
- `restore_file_content(file_path, session)` - Restore files
- `generate_file_diff(file_path, session)` - Generate diffs
- `compare_files(file1, file2)` - Compare files
- `backup_file(file_path)` - Create backups

Split into:
- `file_ops.py` - File operations (42 lines)
- `diff_ops.py` - Diff generation (35 lines)
- `restore_ops.py` - Restoration logic (79 lines)

### 11. Queries Domain (`queries/`)

DuckDB SQL queries for JSONL:

**Query Modules:**
- `session_queries.py` - Session queries
- `find_queries.py` - Find operations
- `blame_queries.py` - Blame queries
- `reflog_queries.py` - Reflog history
- `schema_models.py` - Pydantic normalization

**Key Functions:**
- `get_reflog(jsonl_paths, limit)` - Operation history
- `get_file_history(file_path, jsonl_paths)` - File history
- `query_all_jsonl(jsonl_paths, query)` - Generic query

### 12. Session Domain (`session/`)

```python
from claude_parser.session import SessionManager
```

**SessionManager Class:**
- Manages Claude sessions
- Provides session lifecycle methods

### 13. Storage Domain (`storage/`)

```python
from claude_parser.storage.engine import execute
```

**Storage Functions:**
- `execute(query, params)` - Execute DuckDB SQL
- Single source of truth for database operations

### 14. Tokens Domain (`tokens/`)

```python
from claude_parser.tokens import *
from claude_parser.tokens.context import calculate_context_window
from claude_parser.tokens.billing import calculate_session_cost
```

**Token Functions:**
- `count_tokens(text)` - Count tokens in text
- `analyze_token_usage(session)` - Analyze usage
- `estimate_cost(total_tokens, model)` - Cost estimation
- `token_status(session)` - Current status
- `calculate_context_window(jsonl_path)` - Context usage
- `calculate_session_cost(...)` - Detailed cost calculation

### 15. Watch Domain (`watch/`)

```python
from claude_parser.watch import watch
```

**Real-time Monitoring:**
- `watch(file_path, on_assistant=None, callback=None)` - Watch JSONL files
  - `on_assistant`: Called when assistant messages detected
  - `callback`: Called on any file change

## Usage Patterns

### Complete Session Analysis
```python
from claude_parser import (
    load_latest_session,
    analyze_session,
    analyze_token_usage,
    calculate_session_cost,
    analyze_tool_usage
)
from claude_parser.filtering import filter_pure_conversation

session = load_latest_session()
analysis = analyze_session(session)
tokens = analyze_token_usage(session)
tools = analyze_tool_usage(session)
conversation = filter_pure_conversation(session['messages'])
cost = calculate_session_cost(
    tokens['input_tokens'],
    tokens['output_tokens']
)
```

### Real-time Monitoring
```python
from claude_parser.watch import watch

def on_assistant_message(message):
    print(f"Assistant: {message.get('content', '')[:100]}")

watch(
    "~/.claude/projects/your-project/current.jsonl",
    on_assistant=on_assistant_message
)
```

### Hook Integration
```python
from claude_parser.hooks.api import (
    parse_hook_input,
    allow_operation,
    block_operation
)

hook_data = parse_hook_input()
if hook_data['event'] == 'pre_tool_use':
    if 'rm -rf' in hook_data.get('tool_input', ''):
        block_operation("Dangerous operation detected")
    else:
        allow_operation()
```

### Message Filtering
```python
from claude_parser import load_latest_session, MessageType
from claude_parser.filtering import (
    filter_messages_by_type,
    filter_messages_by_tool,
    exclude_tool_operations
)

session = load_latest_session()
user_msgs = filter_messages_by_type(session['messages'], MessageType.USER)
write_ops = filter_messages_by_tool(session['messages'], 'Write')
pure_conversation = exclude_tool_operations(session['messages'])
```

## Implementation Notes

### LNCA Compliance
- All files < 80 lines of code
- 100% framework delegation
- Single source of truth per feature
- Pydantic for schema normalization

### Framework Usage
- **Typer**: CLI framework
- **Rich**: Terminal formatting
- **DuckDB**: JSONL querying
- **Pydantic**: Data validation
- **Watchfiles**: File monitoring
- **Pathlib**: File operations

### Performance
- Streaming JSONL processing
- Efficient DuckDB queries
- Minimal memory footprint
- Sub-second response times

## Error Handling

All domains use framework error handling:
- Pydantic validates data
- Typer handles CLI errors
- DuckDB manages query errors
- Pathlib validates paths