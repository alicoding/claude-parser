# Claude Parser API Reference

## Overview
Claude Parser provides a Python API for analyzing Claude Code conversations stored in JSONL format. Every API call in Claude Code creates a "commit" with a UUID, allowing Git-like navigation through conversation history.

## Installation
```bash
pip install claude-parser
```

## Core Functions

### Session Management

#### `load_session(jsonl_path: str) -> Dict`
Load a single Claude session from a JSONL file.

```python
from claude_parser import load_session

session = load_session("~/.claude/projects/your-project/session.jsonl")
```

#### `load_latest_session() -> Dict`
Load the most recent Claude session automatically.

```python
from claude_parser import load_latest_session

session = load_latest_session()
```

#### `discover_all_sessions() -> List[Path]`
Discover all Claude session files on the system.

```python
from claude_parser import discover_all_sessions

all_sessions = discover_all_sessions()
```

#### `load_many(*paths) -> List[Dict]`
Load multiple JSONL files at once.

```python
from claude_parser import load_many

sessions = load_many(
    "~/.claude/projects/project1/session1.jsonl",
    "~/.claude/projects/project2/session2.jsonl"
)
```

#### `find_current_transcript() -> Dict`
Alias for `load_latest_session()` - finds the current Claude transcript.

```python
from claude_parser import find_current_transcript

current = find_current_transcript()
```

### Analytics Functions

#### `analyze_session(session: Dict) -> Dict`
Analyze a loaded session for statistics and insights.

```python
from claude_parser import analyze_session, load_latest_session

session = load_latest_session()
analysis = analyze_session(session)
```

#### `analyze_project_contexts(session: Dict) -> Dict`
Analyze project contexts within a session.

```python
from claude_parser import analyze_project_contexts

contexts = analyze_project_contexts(session)
```

#### `analyze_tool_usage(session: Dict) -> Dict`
Analyze tool usage patterns in a session.

```python
from claude_parser import analyze_tool_usage

tool_stats = analyze_tool_usage(session)
```

### Discovery Functions

#### `discover_claude_files() -> List[Path]`
Discover all Claude-related files on the system.

```python
from claude_parser import discover_claude_files

files = discover_claude_files()
```

#### `discover_current_project_files() -> List[Path]`
Discover Claude files for the current project.

```python
from claude_parser import discover_current_project_files

project_files = discover_current_project_files()
```

#### `group_by_projects(files: List[Path]) -> Dict[str, List[Path]]`
Group discovered files by project.

```python
from claude_parser import group_by_projects, discover_claude_files

files = discover_claude_files()
grouped = group_by_projects(files)
```

#### `analyze_project_structure(project_path: str) -> Dict`
Analyze the structure of a specific project.

```python
from claude_parser import analyze_project_structure

structure = analyze_project_structure("/path/to/project")
```

### File Operations

#### `restore_file_content(file_path: str, session: Dict) -> str`
Restore file content from a session.

```python
from claude_parser import restore_file_content

content = restore_file_content("/path/to/file.py", session)
```

#### `generate_file_diff(file_path: str, session: Dict) -> str`
Generate a diff for a file from session history.

```python
from claude_parser import generate_file_diff

diff = generate_file_diff("/path/to/file.py", session)
```

#### `compare_files(file1: str, file2: str) -> str`
Compare two files and generate a diff.

```python
from claude_parser import compare_files

diff = compare_files("file1.py", "file2.py")
```

#### `backup_file(file_path: str) -> str`
Create a backup of a file.

```python
from claude_parser import backup_file

backup_path = backup_file("/path/to/important.py")
```

### Navigation Functions

#### `find_message_by_uuid(uuid: str, session: Dict) -> Dict`
Find a specific message by its UUID.

```python
from claude_parser import find_message_by_uuid

message = find_message_by_uuid("abc123", session)
```

#### `get_message_sequence(start_uuid: str, end_uuid: str, session: Dict) -> List[Dict]`
Get a sequence of messages between two UUIDs.

```python
from claude_parser import get_message_sequence

sequence = get_message_sequence("uuid1", "uuid2", session)
```

#### `get_timeline_summary(session: Dict) -> Dict`
Get a summary of the session timeline.

```python
from claude_parser import get_timeline_summary

timeline = get_timeline_summary(session)
```

### Token Management

#### `count_tokens(text: str) -> int`
Count tokens in a text string.

```python
from claude_parser import count_tokens

token_count = count_tokens("This is some text to analyze")
```

#### `analyze_token_usage(session: Dict) -> Dict`
Analyze token usage in a session.

```python
from claude_parser import analyze_token_usage

token_analysis = analyze_token_usage(session)
```

#### `estimate_cost(total_tokens: int, model: str = None) -> float`
Estimate API cost based on token count.

```python
from claude_parser import estimate_cost

cost = estimate_cost(150000, model="claude-3-opus")
```

#### `token_status(session: Dict) -> Dict`
Get current token usage status.

```python
from claude_parser import token_status

status = token_status(session)
```

#### `calculate_context_window(jsonl_path: str = None) -> Dict`
Calculate context window usage.

```python
from claude_parser import calculate_context_window

context = calculate_context_window("~/.claude/projects/your-project/session.jsonl")
```

#### `calculate_session_cost(input_tokens: int, output_tokens: int, cache_read_tokens: int = 0, cache_creation_tokens: int = 0, model: str = "claude-3-5-sonnet-20241022") -> Dict`
Calculate detailed session cost.

```python
from claude_parser import calculate_session_cost

cost = calculate_session_cost(
    input_tokens=100000,
    output_tokens=50000,
    cache_read_tokens=10000,
    cache_creation_tokens=5000,
    model="claude-3-5-sonnet-20241022"
)
```

### Session Manager

#### `SessionManager`
Class for managing Claude sessions.

```python
from claude_parser import SessionManager

manager = SessionManager()
# Methods available on SessionManager instance
```

### Constants

#### `MessageType`
Enum-like class for message types.

```python
from claude_parser import MessageType

user_messages = [m for m in messages if m['type'] == MessageType.USER]
assistant_messages = [m for m in messages if m['type'] == MessageType.ASSISTANT]
system_messages = [m for m in messages if m['type'] == MessageType.SYSTEM]
```

## Version Information

```python
from claude_parser import __version__

print(__version__)  # "2.0.0"
```

## Common Usage Patterns

### Disaster Recovery
```python
from claude_parser import load_latest_session, restore_file_content

# Recover a deleted file
session = load_latest_session()
content = restore_file_content("/path/to/deleted/file.py", session)
with open("recovered_file.py", "w") as f:
    f.write(content)
```

### Session Analysis
```python
from claude_parser import (
    load_latest_session,
    analyze_session,
    analyze_token_usage,
    calculate_session_cost
)

session = load_latest_session()
analysis = analyze_session(session)
tokens = analyze_token_usage(session)
cost = calculate_session_cost(
    tokens['input_tokens'],
    tokens['output_tokens']
)
```

### Project Discovery
```python
from claude_parser import (
    discover_current_project_files,
    group_by_projects,
    analyze_project_structure
)

files = discover_current_project_files()
grouped = group_by_projects(files)
for project, project_files in grouped.items():
    structure = analyze_project_structure(project)
    print(f"Project: {project}, Files: {len(project_files)}")
```