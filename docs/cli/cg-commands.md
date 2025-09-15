# CG (Claude Git) Command Reference

## Overview
CG treats every Claude API call as a git commit, providing Git-like commands for disaster recovery and session navigation.

## Installation & Usage

```bash
# Install the package
pip install claude-parser

# Run CG commands
python -m claude_parser.cli.cg <command> [options]
```

## Available Commands

### Basic Commands

#### `cg status`
Show current session and project status.

```bash
python -m claude_parser.cli.cg status
```

**Output:**
- Current session file path
- Number of messages
- Session duration
- Token usage summary
- Recent operations

#### `cg log`
Show conversation history (like git log).

```bash
python -m claude_parser.cli.cg log [--limit N]
```

**Options:**
- `--limit, -n`: Number of messages to display (default: 10)

**Output:**
- Message UUIDs (like commit SHAs)
- Timestamps
- Message types (user/assistant)
- Brief content preview

### Advanced Commands

#### `cg find <pattern>`
Search for files matching a pattern across all sessions (like git log --all --grep).

```bash
python -m claude_parser.cli.cg find "test_*.py"
python -m claude_parser.cli.cg find "discovery/core.py"
```

**Arguments:**
- `pattern`: File name pattern to search for

**Output:**
- File paths matching the pattern
- UUIDs where files were accessed
- Operation types (Read, Write, Edit)

#### `cg blame <file_path>`
Show who last modified a file and when.

```bash
python -m claude_parser.cli.cg blame /path/to/file.py
```

**Arguments:**
- `file_path`: Full path to the file

**Output:**
- Last modification UUID
- Timestamp
- Operation type
- Content preview

### Reflog Commands

#### `cg reflog`
Show all operations history (like git reflog).

```bash
python -m claude_parser.cli.cg reflog [--limit N]
```

**Options:**
- `--limit, -n`: Number of entries to display (default: 20)

**Output:**
- Operation UUIDs (shortened to 8 chars)
- Tool names (Read, Write, Edit, Bash, etc.)
- File paths or command details
- Timestamps

#### `cg show <uuid>`
Show details of a specific message or operation (like git show).

```bash
python -m claude_parser.cli.cg show abc123
python -m claude_parser.cli.cg show abc123def456  # Can use partial or full UUID
```

**Arguments:**
- `uuid`: UUID of the message (can be partial, like git commits)

**Output:**
- Full message details
- Message type
- Timestamp
- Tool information (if applicable)
- File content (if it's a file operation)

### Restore Commands

#### `cg checkout <file_path>`
Restore a file to its last known state.

```bash
python -m claude_parser.cli.cg checkout /path/to/deleted/file.py
```

**Arguments:**
- `file_path`: Path to the file to restore

**Output:**
- Confirmation of restoration
- UUID of the version restored
- File content preview

#### `cg restore <uuid>`
Restore files from a specific point in time.

```bash
python -m claude_parser.cli.cg restore abc123
```

**Arguments:**
- `uuid`: UUID of the state to restore to

**Output:**
- List of files restored
- Confirmation messages

### Reset Commands

#### `cg reset <uuid>`
Reset session state to a specific point.

```bash
python -m claude_parser.cli.cg reset abc123
```

**Arguments:**
- `uuid`: UUID to reset to

**Options:**
- `--hard`: Also restore file system state (not just session state)

## Common Workflows

### Disaster Recovery - Lost File
```bash
# 1. Find when the file existed
python -m claude_parser.cli.cg find "important_file.py"

# 2. Check who last modified it
python -m claude_parser.cli.cg blame /path/to/important_file.py

# 3. Restore the file
python -m claude_parser.cli.cg checkout /path/to/important_file.py
```

### Session Investigation
```bash
# 1. View recent operations
python -m claude_parser.cli.cg reflog

# 2. Get details of a specific operation
python -m claude_parser.cli.cg show abc123

# 3. View conversation history
python -m claude_parser.cli.cg log --limit 20
```

### Finding Lost Code
```bash
# 1. Search across all sessions
python -m claude_parser.cli.cg find "test_"

# 2. Show details of where it was found
python -m claude_parser.cli.cg show <uuid_from_find>

# 3. Restore if needed
python -m claude_parser.cli.cg checkout /path/to/test_file.py
```

## Implementation Details

### File Structure
The CG commands are implemented across multiple modules to maintain LNCA compliance (<80 LOC per file):

- `cli/cg.py` - Main command orchestrator
- `cli/cg_basic.py` - Basic commands (status, log)
- `cli/cg_advanced.py` - Advanced commands (find, blame)
- `cli/cg_reflog.py` - Reflog commands (reflog, show)
- `cli/cg_restore.py` - Restore commands (checkout, restore)
- `cli/cg_reset.py` - Reset commands (reset)

### Data Source
All commands query JSONL files stored in:
- `~/.claude/projects/` (default location)
- Current project's `.claude/` directory (if available)

### UUID System
- Every Claude message has a unique UUID
- UUIDs work like git commit SHAs
- Partial UUIDs are supported (first 6-8 characters usually sufficient)
- UUIDs enable time-travel through conversation history

## Error Handling

Common error messages and solutions:

- **"No Claude sessions found"**: No JSONL files in the expected locations
- **"UUID not found"**: The specified UUID doesn't exist in any session
- **"File not found in history"**: The file path has never been accessed in recorded sessions
- **"Multiple matches found"**: Partial UUID matches multiple messages, use more characters

## Performance Notes

- Commands use DuckDB for efficient JSONL querying
- Large sessions (>100MB) may take a few seconds to process
- Results are not cached between commands (each command reads fresh data)
- File operations use Pydantic for schema normalization