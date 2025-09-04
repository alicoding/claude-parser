# CG: Git-like Interface for Claude Code

The `cg` command provides a git-like interface for navigating and managing Claude Code conversation history with complete project isolation.

## Overview

`cg` works exactly like `git` - it automatically detects which Claude Code project you're working in based on your current working directory and operates only on that project's history.

## Core Features

### 🎯 Perfect Project Isolation

- **Automatic Project Detection**: Just like `git` finds `.git` directories, `cg` finds your Claude Code project
- **No Cross-Contamination**: Operations from other projects are completely filtered out
- **Directory-Based**: Works from any subdirectory within your project

```bash
# Works from project root
cd /path/to/my-project
cg status

# Works from subdirectories too
cd /path/to/my-project/src/components
cg status  # Still shows my-project operations only
```

### 🕐 Time Travel Commands

Navigate through your Claude Code conversation history:

```bash
# View current project status
cg status
cg status --sessions  # Multi-session view

# Browse operation history
cg log
cg log --file app.py   # Operations on specific file
cg log --limit 10      # Last 10 operations

# Go back in time
cg undo 3              # Undo last 3 operations
cg undo --to abc12345  # Go to specific UUID (partial UUIDs work!)

# Check specific states
cg checkout def67890   # View files at specific operation
cg show abc12345       # Show details of specific operation

# Compare changes
cg diff                # Recent changes
cg diff --uuid abc123  # Changes from specific operation
cg diff --range abc123..def456  # Compare two points
```

## How Project Isolation Works

### Discovery Process

1. **Current Directory Detection**: Uses `cwd` to determine where you are
2. **Project Matching**: Finds the corresponding Claude Code project in `~/.claude/projects/`
3. **Operation Filtering**: Only loads operations that affect files within your project

### Example Scenario

```bash
# You have multiple projects
~/projects/
├── web-app/           # Claude project A
├── api-service/       # Claude project B
└── mobile-app/        # Claude project C

# Running cg from web-app shows only web-app operations
cd ~/projects/web-app
cg log
# ✅ Shows: Write src/App.js, Edit package.json, etc.
# ❌ Filters out: api-service operations, mobile-app operations

cd ~/projects/api-service
cg log
# ✅ Shows: Write server.py, Edit requirements.txt, etc.
# ❌ Filters out: web-app operations, mobile-app operations
```

## Installation & Setup

```bash
# Install claude-parser with cg support
pip install claude-parser[cg]

# Verify installation
cg --help
```

## Command Reference

### Status Commands
- `cg status` - Show current project state
- `cg status --sessions` - Multi-session summary

### History Commands
- `cg log` - Show operation history
- `cg log --file <file>` - Operations on specific file
- `cg log --limit <n>` - Limit output
- `cg log --sessions` - Group by session

### Navigation Commands
- `cg checkout <uuid>` - View state at specific operation
- `cg undo <n>` - Go back N operations
- `cg undo --to <uuid>` - Go to specific operation
- `cg show <uuid>` - Show operation details

### Comparison Commands
- `cg diff` - Show recent changes
- `cg diff --uuid <uuid>` - Show changes from operation
- `cg diff --range <uuid1>..<uuid2>` - Compare two states

## Technical Implementation

### UUID Expansion
- Full UUIDs: `abc12345-1234-5678-9012-123456789abc`
- Partial UUIDs: `abc12345` (automatically expanded)
- Both formats work in all commands

### File Path Resolution
```python
# Operations are filtered by project path
def _is_operation_in_project(self, operation: Dict) -> bool:
    file_path = operation.get("file_path")
    if not file_path:
        return False

    try:
        file_abs_path = Path(file_path).resolve()
        return file_abs_path.is_relative_to(self.project_path)
    except (ValueError, OSError):
        return str(self.project_path) in file_path
```

### Multi-Session Support
- Loads all JSONL files for the project
- Sorts operations chronologically across sessions
- Maintains complete history across multiple Claude conversations

## Integration with CI/CD

The `cg` commands are fully testable and integrate with CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Test CG Commands
  run: |
    # Test basic functionality
    python -m pytest tests/test_cg_cli.py
    python -m pytest tests/test_claude_code_timeline.py

    # Test with real data (if available)
    cg status || echo "No Claude transcripts (expected in CI)"
```

## Comparison with Git

| Feature | Git | CG (Claude Git) |
|---------|-----|-----------------|
| **Project Detection** | `.git` folder | Claude project discovery |
| **History Navigation** | `git log`, `git show` | `cg log`, `cg show` |
| **Time Travel** | `git checkout <commit>` | `cg checkout <uuid>` |
| **Undo Changes** | `git reset HEAD~n` | `cg undo n` |
| **Compare States** | `git diff` | `cg diff` |
| **Current Status** | `git status` | `cg status` |
| **Isolation** | Repository boundaries | Project path boundaries |

## Examples

### Daily Workflow
```bash
# Morning: Check what happened yesterday
cg log --limit 20

# See current state
cg status

# Check a specific change
cg show abc12345

# If something broke, go back
cg undo --to def67890

# Compare before/after
cg diff --range def67890..abc12345
```

### Debugging Session
```bash
# Something is broken, when did it work?
cg log --file src/main.py

# Go back to when it worked
cg checkout xyz98765

# Compare what changed
cg diff --range xyz98765..HEAD
```

### Code Review
```bash
# Show recent changes for review
cg diff

# Show details of specific operation
cg show abc12345

# Check all operations in session
cg log --sessions
```

## Best Practices

1. **Work in Project Directories**: Always run `cg` from within your project
2. **Use Partial UUIDs**: `abc12345` is easier than full UUIDs
3. **Regular Status Checks**: `cg status` shows your current position
4. **Combine Commands**: `cg log | head -5` to see recent operations

## Troubleshooting

### "No Claude Code transcripts found"
- Make sure you're in a directory that Claude has worked on
- Check `ls ~/.claude/projects` to see available projects
- Ensure the project path matches what's in the JSONL files

### "Cannot restore to UUID"
- Use `cg log` to see available UUIDs
- Partial UUIDs work: `abc12345` instead of full UUID
- Check if the UUID exists in current project (not another project)

### Operations from Other Projects
- This should not happen with the new project isolation
- If you see cross-contamination, it's a bug - please report it

## Future Enhancements

- **Branch-like Sessions**: `cg branch <session-name>`
- **Merge Operations**: Combine operations from multiple sessions
- **Diff Visualization**: Enhanced diff output with syntax highlighting
- **Operation Annotations**: Add comments to operations
