# Claude Parser

A Python library for parsing and analyzing Claude Code's JSONL conversation logs.

## Features

- **Parse JSONL**: Load and parse Claude's conversation format
- **Timeline**: Git-like navigation through conversation history
- **Recovery**: Restore deleted files from JSONL history
- **Analysis**: Extract patterns and insights from conversations
- **Hooks**: Integration with Claude Code's hook system

## Installation

```bash
pip install -e .
```

## Quick Start

```python
from claude_parser import load

# Load a conversation
conv = load("path/to/conversation.jsonl")

# Access messages
for msg in conv.messages:
    print(f"{msg.type}: {msg.content[:50]}...")

# Search content
results = conv.search("error")
```

## Timeline - Git for JSONL

```python
from claude_parser.timeline import Timeline

# Create timeline from JSONL
timeline = Timeline(Path("~/.claude/projects/"))

# Checkout any point in time
state = timeline.checkout("2024-08-23T10:00:00")

# Create branches
timeline.branch("before-refactor")

# Diff between states
changes = timeline.diff("branch:main", "branch:feature")
```

## Recovery

Recover deleted projects from JSONL:

```python
timeline = Timeline(jsonl_dir)
timeline.recover(
    output_dir="/safe/location/",
    project="my-project"
)
```

## Development

```bash
# Install development dependencies
poetry install

# Run tests
pytest

# Check for secrets before committing
python security_scan.py
```

## Security

- Never commit `.env` files
- Use `.env.example` as template
- Run `security_scan.py` before pushing

## License

MIT

## Author

Ali Al Dallal (ali@alicoding.com)