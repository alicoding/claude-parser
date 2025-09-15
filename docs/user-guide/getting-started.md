# Getting Started with Claude Parser

## What is Claude Parser?

Claude Parser is a disaster recovery and analysis tool for Claude Code conversations. It provides Git-like commands to navigate through your conversation history, recover lost files, and analyze your Claude usage.

## Installation

```bash
pip install claude-parser
```

## Quick Start

### 1. Find Your Current Session

```python
from claude_parser import load_latest_session

session = load_latest_session()
print(f"Loaded session with {len(session['messages'])} messages")
```

### 2. Use CG Commands for Recovery

```bash
# Check current status
python -m claude_parser.cli.cg status

# View recent operations
python -m claude_parser.cli.cg reflog

# Find a lost file
python -m claude_parser.cli.cg find "important_file.py"

# Restore it
python -m claude_parser.cli.cg checkout /path/to/important_file.py
```

## Core Use Cases

### Disaster Recovery - "Claude Deleted My Files!"

When Claude accidentally deletes or overwrites important files:

```bash
# Step 1: Find when the file existed
python -m claude_parser.cli.cg find "deleted_file.py"

# Output: Shows UUIDs where file was accessed
# Found in message abc123def: Write /path/to/deleted_file.py

# Step 2: Restore the file
python -m claude_parser.cli.cg checkout /path/to/deleted_file.py

# File restored from session abc123def
```

### Session Analysis - Understanding Token Usage

```python
from claude_parser import (
    load_latest_session,
    analyze_token_usage,
    calculate_session_cost
)

session = load_latest_session()
tokens = analyze_token_usage(session)

print(f"Input tokens: {tokens['input_tokens']}")
print(f"Output tokens: {tokens['output_tokens']}")
print(f"Total tokens: {tokens['total_tokens']}")

# Calculate cost
cost = calculate_session_cost(
    input_tokens=tokens['input_tokens'],
    output_tokens=tokens['output_tokens']
)
print(f"Estimated cost: ${cost['total_cost']:.2f}")
```

### Project Discovery - Finding All Claude Files

```python
from claude_parser import (
    discover_current_project_files,
    group_by_projects
)

# Find all Claude files for current project
project_files = discover_current_project_files()
print(f"Found {len(project_files)} Claude session files")

# Group by projects
all_files = discover_claude_files()
grouped = group_by_projects(all_files)

for project, files in grouped.items():
    print(f"{project}: {len(files)} sessions")
```

### Navigation - Time Travel Through Conversations

```python
from claude_parser import (
    find_message_by_uuid,
    get_message_sequence,
    get_timeline_summary
)

session = load_latest_session()

# Find specific message
message = find_message_by_uuid("abc123", session)

# Get sequence between two points
sequence = get_message_sequence("uuid1", "uuid2", session)

# Get timeline overview
timeline = get_timeline_summary(session)
```

## Working with File Operations

### Comparing Files

```python
from claude_parser import compare_files

diff = compare_files("version1.py", "version2.py")
print(diff)
```

### Generating Diffs from History

```python
from claude_parser import generate_file_diff

session = load_latest_session()
diff = generate_file_diff("/path/to/file.py", session)
print(diff)
```

### Backing Up Important Files

```python
from claude_parser import backup_file

backup_path = backup_file("/path/to/critical.py")
print(f"Backed up to: {backup_path}")
```

## Advanced Usage

### Loading Multiple Sessions

```python
from claude_parser import load_many

sessions = load_many(
    "~/.claude/projects/project1/session1.jsonl",
    "~/.claude/projects/project2/session2.jsonl",
    "~/.claude/projects/project3/session3.jsonl"
)

for i, session in enumerate(sessions):
    print(f"Session {i+1}: {len(session['messages'])} messages")
```

### Custom Message Filtering

```python
from claude_parser import MessageType

session = load_latest_session()

# Filter by message type
user_messages = [
    msg for msg in session['messages']
    if msg.get('type') == MessageType.USER
]

assistant_messages = [
    msg for msg in session['messages']
    if msg.get('type') == MessageType.ASSISTANT
]

print(f"User messages: {len(user_messages)}")
print(f"Assistant messages: {len(assistant_messages)}")
```

### Analyzing Tool Usage Patterns

```python
from claude_parser import analyze_tool_usage

session = load_latest_session()
tool_stats = analyze_tool_usage(session)

# Show most used tools
for tool, count in tool_stats['tool_counts'].items():
    print(f"{tool}: {count} uses")
```

## Common Workflows

### Daily Standup Report

```python
from claude_parser import (
    load_latest_session,
    analyze_session,
    analyze_tool_usage
)
from datetime import datetime

session = load_latest_session()
analysis = analyze_session(session)

print(f"Session Date: {datetime.now().date()}")
print(f"Messages: {analysis['message_count']}")
print(f"Duration: {analysis['duration']}")

tools = analyze_tool_usage(session)
print(f"Files edited: {tools['tool_counts'].get('Edit', 0)}")
print(f"Files created: {tools['tool_counts'].get('Write', 0)}")
print(f"Commands run: {tools['tool_counts'].get('Bash', 0)}")
```

### Finding All Test Files

```bash
# Find all test files across all sessions
python -m claude_parser.cli.cg find "test_*.py"

# Find specific test
python -m claude_parser.cli.cg find "test_discovery.py"
```

### Investigating Errors

```bash
# See what happened recently
python -m claude_parser.cli.cg reflog --limit 50

# Check specific operation that might have caused issues
python -m claude_parser.cli.cg show abc123

# See full conversation context
python -m claude_parser.cli.cg log --limit 20
```

## Tips and Best Practices

### 1. Regular Status Checks
Run `cg status` regularly to understand your current session state.

### 2. Use Partial UUIDs
Like git, you only need the first 6-8 characters of a UUID:
```bash
python -m claude_parser.cli.cg show abc123  # Instead of full UUID
```

### 3. Combine Commands
Use command combinations for investigation:
```bash
# Find → Show → Checkout workflow
python -m claude_parser.cli.cg find "lost.py"
python -m claude_parser.cli.cg show <uuid>
python -m claude_parser.cli.cg checkout /path/to/lost.py
```

### 4. Monitor Token Usage
```python
from claude_parser import calculate_context_window

context = calculate_context_window()
if context['total_tokens'] > 180000:
    print("Warning: Approaching context limit!")
```

### 5. Project Organization
Keep your Claude sessions organized:
```python
from claude_parser import analyze_project_structure

structure = analyze_project_structure("/your/project")
# Understand how Claude sees your project
```

## Troubleshooting

### "No Claude sessions found"
- Check that Claude Code is installed
- Verify sessions exist in `~/.claude/projects/`
- Try using absolute paths

### "UUID not found"
- Use `cg reflog` to see available UUIDs
- Try with more characters if partial match fails
- Check you're in the right project directory

### "File not found in history"
- File may never have been accessed by Claude
- Try searching with different patterns
- Check the full path is correct

### Performance Issues
- Large sessions (>100MB) may be slow
- Use `--limit` to reduce output
- Consider splitting very long sessions

## Next Steps

- Explore the [API Reference](../api/reference.md) for all available functions
- Learn about [CG Commands](../cli/cg-commands.md) in detail
- Understand the [Architecture](../architecture/system-design.md)