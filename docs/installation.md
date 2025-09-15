# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Claude Code installed on your system (generates the JSONL files)

## Quick Install

```bash
pip install claude-parser
```

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
# Standard installation
pip install claude-parser

# With all optional dependencies
pip install claude-parser[all]
```

### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/alicoding/claude-parser.git
cd claude-parser

# Install in development mode
pip install -e .
```

### 3. Install with Poetry

```bash
# If you use Poetry for dependency management
poetry add claude-parser
```

### 4. Install with pipx (Isolated Environment)

```bash
# For CLI tools only
pipx install claude-parser
```

## Verify Installation

### Check Version
```python
import claude_parser
print(claude_parser.__version__)  # Should show "2.0.0"
```

### Test CLI Commands
```bash
# Test CG (Claude Git) commands
python -m claude_parser.cli.cg --help
python -m claude_parser.cli.cg status

# Test CH (Claude Hooks) command
python -m claude_parser.cli.ch --help
```

### Test Python API
```python
from claude_parser import load_latest_session

try:
    session = load_latest_session()
    print(f"✓ Found session with {len(session['messages'])} messages")
except FileNotFoundError:
    print("No Claude sessions found - this is normal if Claude Code hasn't been used yet")
```

## Quick Start - First Commands

### 1. Check Current Status
```bash
python -m claude_parser.cli.cg status
```

### 2. View Recent Operations
```bash
python -m claude_parser.cli.cg reflog
```

### 3. Search for Files
```bash
python -m claude_parser.cli.cg find "*.py"
```

### 4. Load Session in Python
```python
from claude_parser import load_latest_session, analyze_session

session = load_latest_session()
analysis = analyze_session(session)
print(f"Session has {analysis['message_count']} messages")
```

## File Locations

Claude Parser looks for JSONL files in these locations:

### Default Location (Claude Code)
```
~/.claude/projects/
```

### Project-Specific Location
```
/your/project/.claude/
```

### Custom Location
```python
from claude_parser import load_session
session = load_session("/custom/path/to/session.jsonl")
```

## Optional Configuration

### For CH (Claude Hooks)

Set default executor for hooks:
```bash
export CLAUDE_HOOK_EXECUTOR=lnca_plugins
```

### For Custom Paths

```python
# Load from specific location
from claude_parser import load_session
session = load_session("/my/custom/path/session.jsonl")
```

## Dependencies

These are installed automatically:
- **typer** - CLI framework
- **rich** - Terminal formatting
- **duckdb** - JSONL querying
- **pydantic** - Data validation
- **watchfiles** - File monitoring (optional)

## Platform-Specific Notes

### macOS
- Works out of the box
- Default path: `~/.claude/projects/`

### Linux
- May need to install python3-pip first: `sudo apt-get install python3-pip`
- Default path: `~/.claude/projects/`

### Windows
- Use PowerShell or Windows Terminal
- Default path: `%USERPROFILE%\.claude\projects\`
- Use forward slashes in Python: `C:/Users/name/.claude/projects/...`

## Virtual Environment Setup (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install claude-parser
pip install claude-parser
```

## Development Installation

For contributing:

```bash
# Clone and install in development mode
git clone https://github.com/alicoding/claude-parser.git
cd claude-parser
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code style
ruff check claude_parser/
```

## Troubleshooting

### "No module named 'claude_parser'"
```bash
# Reinstall
pip install --force-reinstall claude-parser
```

### "No Claude sessions found"
- Make sure Claude Code has been used and created sessions
- Check `~/.claude/projects/` exists
- Try specifying the path explicitly

### DuckDB Import Error
```bash
# Install duckdb separately
pip install duckdb
```

### Permission Errors
```bash
# Install for current user only
pip install --user claude-parser
```

## Upgrading

```bash
# Upgrade to latest version
pip install --upgrade claude-parser
```

## Uninstalling

```bash
pip uninstall claude-parser
```

## Next Steps

1. Read the [Getting Started Guide](user-guide/getting-started.md)
2. Try the [disaster recovery workflow](user-guide/getting-started.md#disaster-recovery---claude-deleted-my-files)
3. Explore [CLI Commands](cli/commands.md)
4. Check the [Complete API Reference](api/complete-reference.md)

## Getting Help

- GitHub Issues: https://github.com/alicoding/claude-parser/issues
- Documentation: https://github.com/alicoding/claude-parser