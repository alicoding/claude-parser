# Complete CLI Command Reference

Claude Parser provides two main CLI tools:
- **CG (Claude Git)**: Git-like commands for session navigation and recovery
- **CH (Claude Hooks)**: Composable hook runner for Claude Code integrations

## CG Commands - Git-like Interface

### Installation
```bash
pip install claude-parser
```

### Basic Usage
```bash
python -m claude_parser.cli.cg <command> [options]
```

### Available CG Commands

#### Session Information
- `cg status` - Show current session status and statistics
- `cg log [--limit N]` - Show conversation history

#### Search and Discovery
- `cg find <pattern>` - Search for files across all sessions
- `cg blame <file_path>` - Show last modification info for a file

#### History Navigation
- `cg reflog [--limit N]` - Show all operations history
- `cg show <uuid>` - Show details of specific message/operation

#### File Recovery
- `cg checkout <file_path>` - Restore file to last known state
- `cg restore <uuid>` - Restore files from specific point in time

#### Session Management
- `cg reset <uuid> [--hard]` - Reset to specific session state

### CG Examples

```bash
# Find lost test files
python -m claude_parser.cli.cg find "test_*.py"

# Check who last modified a file
python -m claude_parser.cli.cg blame /path/to/file.py

# View operation history
python -m claude_parser.cli.cg reflog --limit 30

# Restore a deleted file
python -m claude_parser.cli.cg checkout /path/to/deleted.py

# Show details of an operation
python -m claude_parser.cli.cg show abc123
```

## CH Commands - Composable Hook System

### Basic Usage
```bash
python -m claude_parser.cli.ch run [options]
```

### Available CH Commands

#### run
Execute hooks with pluggable executors.

```bash
python -m claude_parser.cli.ch run --executor <module>
```

**Options:**
- `--executor, -e <module>`: Plugin executor module (e.g., lnca_plugins)
- Can also use environment variable: `CLAUDE_HOOK_EXECUTOR`

### How CH Works

1. **Input**: Reads hook data from stdin (provided by Claude Code)
2. **Processing**: Executes with specified executor module
3. **Output**: Returns results per Anthropic hook specification

### CH Configuration

#### Environment Variables
```bash
# Set default executor
export CLAUDE_HOOK_EXECUTOR=lnca_plugins

# Now ch will use this executor by default
python -m claude_parser.cli.ch run
```

#### Direct Execution
```bash
# Specify executor directly
python -m claude_parser.cli.ch run --executor custom_executor
```

### Hook Event Types

CH handles these Claude Code hook events:
- `pre_tool_use` - Before tool execution
- `post_tool_use` - After tool execution
- `user_prompt_submit` - User message submission
- `stop` - Session stop
- `notification` - System notifications
- `session_start` - Session initialization
- `session_end` - Session termination

### Creating Custom Executors

Executors are Python modules that implement hook handling:

```python
# my_executor.py
def execute_hooks(hook_data):
    """Process hook data and return response"""
    event_type = hook_data.get('event')

    if event_type == 'pre_tool_use':
        # Validate tool usage
        return {'action': 'allow'}

    return {'action': 'allow'}
```

### CH Integration with Claude Code

1. **Configure Claude Code settings** to use CH:
```json
{
  "hooks": {
    "pre_tool_use": "python -m claude_parser.cli.ch run --executor my_executor"
  }
}
```

2. **Set environment variable** for default executor:
```bash
export CLAUDE_HOOK_EXECUTOR=my_executor
```

3. **Test hook execution**:
```bash
echo '{"event": "pre_tool_use", "tool": "Write"}' | python -m claude_parser.cli.ch run
```

## Command Implementation Details

### File Organization (LNCA Compliant)

All CLI files are under 80 lines of code:

#### CG Command Files
- `cli/cg.py` (34 lines) - Main orchestrator
- `cli/cg_basic.py` (67 lines) - Status, log
- `cli/cg_advanced.py` (69 lines) - Find, blame
- `cli/cg_reflog.py` (80 lines) - Reflog, show
- `cli/cg_restore.py` (61 lines) - Checkout, restore
- `cli/cg_reset.py` (63 lines) - Reset

#### CH Command Files
- `cli/ch.py` (48 lines) - Composable hook runner

### Data Sources

- **CG**: Queries JSONL files in `~/.claude/projects/`
- **CH**: Processes stdin input from Claude Code hooks

### Framework Delegation

Both commands use 100% framework delegation:
- **Typer**: CLI framework and argument parsing
- **Rich**: Terminal output formatting
- **DuckDB**: JSONL querying (CG only)
- **Pydantic**: Data validation and normalization

## Performance Notes

- **CG**: Queries use DuckDB for efficient JSONL processing
- **CH**: Minimal overhead, passes through when no executor specified
- Both tools start in < 1 second

## Error Handling

### CG Common Errors
- "No Claude sessions found" - Check JSONL file locations
- "UUID not found" - Use partial UUID or check with reflog
- "File not found in history" - File may not have been accessed

### CH Common Errors
- "No executor specified" - Set CLAUDE_HOOK_EXECUTOR or use --executor
- "Module not found" - Ensure executor module is in Python path
- "Invalid hook data" - Check stdin input format

## Advanced Usage

### Combining CG Commands
```bash
# Find → Show → Checkout workflow
python -m claude_parser.cli.cg find "config.py"
python -m claude_parser.cli.cg show abc123
python -m claude_parser.cli.cg checkout /path/to/config.py
```

### Chaining CH with Other Tools
```bash
# Process hook and log results
echo '{"event": "pre_tool_use"}' | \
  python -m claude_parser.cli.ch run --executor validator | \
  tee hook_log.json
```

### Scripting with Both Tools
```python
import subprocess
import json

# Use CG to find files
result = subprocess.run(
    ["python", "-m", "claude_parser.cli.cg", "find", "test_"],
    capture_output=True, text=True
)

# Use CH to validate operations
hook_data = {"event": "pre_tool_use", "tool": "Write"}
process = subprocess.Popen(
    ["python", "-m", "claude_parser.cli.ch", "run", "--executor", "validator"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
)
output, _ = process.communicate(json.dumps(hook_data))
```