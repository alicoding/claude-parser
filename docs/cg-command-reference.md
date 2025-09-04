# `cg` Command Reference 🎯

> **Git-like interface for navigating Claude Code conversations and file operations**

The `cg` (claude-git) command provides an intuitive, git-style interface for navigating your Claude Code operations across multiple sessions with zero configuration needed.

## 🚀 Quick Start

### System Requirements
- **Supported**: macOS, Linux (Unix-like systems)
- **Requirements**: Claude Code installed with active projects in `~/.claude/projects`
- **Python**: 3.9+ with claude-parser installed

### Installation & Setup

```bash
# Install claude-parser
pip install claude-parser

# Verify Claude Code setup
ls ~/.claude/projects
# Should show directories like: -Volumes-Dev-my-project

# Test cg command from any project directory
cd /your/project
cg status
# Should auto-detect and show project status
```

## 🎮 Core Commands

### Project Status & Information

#### `cg status`
Show current project state and multi-session information.

```bash
# Basic project status
cg status
# 📊 Timeline Summary (12 operations from 1 session)
# 📂 Project: /Users/dev/my-app
#   📄 app.py: 5 operations
#   📄 config.py: 3 operations

# Multi-session detailed view
cg status --sessions
# 📊 Multi-Session Summary
#    Sessions: 2
#    Operations: 8
#    Project: /Users/dev/my-app
#    📋 Session abc12345: 4 ops → app.py, config.py
#    📋 Session def67890: 4 ops → utils.py, tests.py
```

#### `cg log`
View operation history across all Claude Code sessions.

```bash
# Recent operations across all files and sessions
cg log
# 📊 Timeline Summary (15 operations from 2 sessions)
# 📂 Project: /Users/dev/my-app
#   📄 app.py: 6 operations
#   📄 config.py: 4 operations
#   📄 utils.py: 5 operations
# 🔀 Multi-session detected:
#   📋 Session abc12345: 8 operations
#   📋 Session def67890: 7 operations

# Specific file history across all sessions
cg log --file app.py
# 📅 Timeline for app.py (6 operations)
#    1. a1b2c3d4 (Read) [abc12345] 2025-01-04T10:15:30
#    2. e5f6g7h8 (Edit) [abc12345] 2025-01-04T10:16:45
#    3. i9j0k1l2 (Edit) [def67890] 2025-01-04T10:17:20
#    4. m3n4o5p6 (MultiEdit) [abc12345] 2025-01-04T10:18:10
#    5. q7r8s9t0 (Edit) [def67890] 2025-01-04T10:19:30
#    6. u1v2w3x4 (Edit) [abc12345] 2025-01-04T10:20:45
```

### Time Travel & Restoration

#### `cg checkout <uuid>`
Restore files to the exact state at a specific UUID operation.

```bash
# Restore to specific operation
cg checkout e5f6g7h8
# ✅ Restored to UUID e5f6g7h8
#   📄 app.py (1,234 chars)
#   📄 config.py (567 chars)

# Using partial UUID (first 8 characters)
cg checkout e5f6g7h8
# Same result - auto-expands to full UUID
```

#### `cg undo <n>`
Go back N operations from the current state (across all files and sessions).

```bash
# Undo last operation (any file, any session)
cg undo
# ✅ Undid 1 change(s)
# 📄 Restored: app.py
# 🆔 UUID: e5f6g7h8
# 🔧 Operation: Edit

# Undo multiple operations
cg undo 3
# ✅ Undid 3 change(s)
# 📄 Restored: config.py
# 🆔 UUID: a1b2c3d4
# 🔧 Operation: Write

# Undo to specific UUID
cg undo --to i9j0k1l2
# ✅ Restored to UUID i9j0k1l2
#   📄 app.py (890 chars)
```

### Analysis & Comparison

#### `cg show <uuid>`
Show detailed information about a specific operation.

```bash
cg show e5f6g7h8
# 🔍 Operation e5f6g7h8
#    Type: Edit
#    File: app.py
#    Session: abc12345
#    Timestamp: 2025-01-04T10:16:45
#    Changes: print("hello") → print("world")
```

#### `cg diff`
Show differences between operations or states.

```bash
# Show recent changes
cg diff
# Shows changes from previous operation to current

# Compare two specific operations
cg diff a1b2c3d4..e5f6g7h8
# Shows exact file differences between UUIDs

# Show what changed at specific operation
cg diff --uuid e5f6g7h8
# 🔍 Changes at e5f6g7h8 (Edit on app.py)
# - print("hello")
# + print("world")
```

### Navigation & Steps

#### `cg reset <uuid>`
Reset to a specific operation (like `git reset`).

```bash
# Reset to specific state
cg reset e5f6g7h8
# ✅ Reset to UUID e5f6g7h8 - Edit app.py

# Reset with confirmation for destructive changes
cg reset --hard a1b2c3d4
# ⚠️  This will lose 5 operations after a1b2c3d4
# Continue? [y/N]: y
# ✅ Hard reset to UUID a1b2c3d4
```

#### `cg steps <file> <n>`
Navigate N steps in a specific file's history.

```bash
# Go to step 3 in app.py's history
cg steps app.py 3
# 📍 Step 3/6 for app.py
# 🆔 UUID: i9j0k1l2
# 📝 Content: def main():\n    print("step 3")...

# Navigate relative to current position
cg steps app.py +2  # Forward 2 steps
cg steps app.py -1  # Back 1 step
```

## 🔍 Advanced Usage

### Multi-Session Workflows

#### Understanding Sessions
Each time Claude Code starts, it creates a new session with a unique ID. The `cg` command tracks all sessions that have worked on your project.

```bash
# See all sessions that touched this project
cg status --sessions
# 📊 Multi-Session Summary
#    Sessions: 3
#    Operations: 24
#    📋 Session abc12345: 8 ops → app.py, config.py
#    📋 Session def67890: 10 ops → utils.py, app.py
#    📋 Session ghi34567: 6 ops → tests.py, config.py
```

#### Session-Aware Operations
All commands work across sessions automatically - you don't need to specify which session an operation came from.

```bash
# This shows operations from ALL sessions chronologically
cg log --file app.py
# Timeline includes operations from sessions abc12345 AND def67890

# Undo works across sessions too
cg undo 5
# Will go back 5 operations regardless of which session created them
```

### Branch Operations
The `cg` command leverages the underlying git repository that tracks your operations.

```bash
# List branches (git branches in the timeline repository)
cg branch
# * main
#   session-experiment
#   feature-test

# Create branch at current operation
cg branch new-feature
# Created branch 'new-feature' at current operation

# Switch branches
cg checkout new-feature
# Switched to branch 'new-feature'

# Merge branches
cg merge session-experiment
# Merged 'session-experiment' into current branch
```

### Filtering & Search

```bash
# Show only Edit operations
cg log --operation Edit

# Show operations in date range
cg log --since "2025-01-04" --until "2025-01-05"

# Show operations by specific session
cg log --session abc12345
```

## 🎯 Real-World Scenarios

### Scenario 1: "What Did Claude Just Do?"

```bash
# After a complex Claude Code session
cg status
# Shows summary of all changes

cg log --limit 5
# Shows last 5 operations across all files

# See what the last operation changed
cg diff
# Shows exact changes from last operation
```

### Scenario 2: "Multiple Sessions Conflict"

```bash
# Two Claude sessions modified the same file
cg log --file config.py
# 📅 Timeline for config.py (8 operations)
#    1. a1b2c3d4 (Write) [abc12345] 2025-01-04T10:00:00
#    2. e5f6g7h8 (Edit) [abc12345] 2025-01-04T10:01:00
#    3. i9j0k1l2 (Edit) [def67890] 2025-01-04T10:01:30  ← Session B
#    4. m3n4o5p6 (Edit) [abc12345] 2025-01-04T10:02:00  ← Session A
#    ...

# Go back to before the conflict
cg checkout e5f6g7h8  # Before session B's changes
```

### Scenario 3: "Find Specific Change"

```bash
# Look for when a specific function was added
cg log --file utils.py
# Browse through UUIDs

cg show m3n4o5p6
# 🔍 Operation m3n4o5p6
#    Changes: +def helper_function():

# Go to that state
cg checkout m3n4o5p6
```

### Scenario 4: "Undo Multiple Files"

```bash
# Last 3 operations affected multiple files
cg undo 3
# ✅ Undid 3 change(s)
# 📄 Restored: app.py, config.py, utils.py
# 🆔 Back to UUID: a1b2c3d4

# Check what was restored
cg status
# Shows current state after undo
```

## ⚙️ Configuration

### Auto-Detection
The `cg` command automatically:
- Detects your current project from the working directory
- Finds the matching `~/.claude/projects/` directory
- Loads all JSONL files (sessions) for that project
- Aggregates operations chronologically across sessions

### Manual Project Specification
```bash
# Work with specific project (if auto-detection fails)
cg --project /specific/path status

# Use different Claude directory
cg --claude-dir /custom/claude/location status
```

### Output Formatting
```bash
# JSON output for scripting
cg log --format json

# Minimal output
cg log --oneline

# Full verbose output
cg log --verbose
```

## 🔧 Troubleshooting

### Common Issues

#### "No Claude Code sessions found"
```bash
# Check Claude Code directory
ls ~/.claude/projects
# Should show project directories

# Verify you're in a Claude-worked project
pwd
# Make sure this directory has been used with Claude Code

# Check if JSONL files exist
ls ~/.claude/projects/*/
# Should show .jsonl files
```

#### "Cannot restore to UUID"
```bash
# Verify UUID exists in history
cg log | grep e5f6g7h8
# UUID should appear in the output

# Use exact UUID from cg log output
cg log --format full
# Copy full UUID, not abbreviated one
```

#### "Auto-detection failed"
```bash
# Check current directory path encoding
pwd
# Compare with ls ~/.claude/projects output

# Try manual project specification
cg --project $(pwd) status
```

### Debug Mode
```bash
# Enable verbose logging
cg --verbose status
# Shows detailed project detection and session loading

# Show raw operation data
cg log --debug
# Shows internal operation structure
```

## 📊 Performance

### Large Projects
The `cg` command is optimized for projects with many operations:
- **Lazy loading**: Only loads operations when needed
- **Caching**: Git repository operations are cached
- **Efficient search**: Fast UUID lookups and filtering

### Memory Usage
```bash
# Check operation count
cg status
# Shows total operations loaded

# For very large projects (1000+ operations)
cg log --limit 50  # Limit output for performance
```

## 🔗 Integration

### Shell Aliases
Add convenient aliases to your shell profile:

```bash
# In ~/.bashrc or ~/.zshrc
alias undo='cg undo'
alias cstatus='cg status'
alias clog='cg log'

# Quick undo shortcuts
alias undo1='cg undo 1'
alias undo3='cg undo 3'
alias undo5='cg undo 5'
```

### Git Integration
The `cg` command creates real git repositories, so you can use git commands too:

```bash
# The timeline repository is at ~/.claude/projects/[project]/timeline/
cd ~/.claude/projects/-your-project-path/timeline/

# Use regular git commands
git log --oneline
git show <commit>
git checkout <commit>
```

## 📚 See Also

- [Multi-Session Guide](multi-session-guide.md) - Detailed multi-session workflow examples
- [Architecture](architecture.md) - Technical implementation details
- [API Reference](../api-reference.md) - Python API for programmatic usage
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
