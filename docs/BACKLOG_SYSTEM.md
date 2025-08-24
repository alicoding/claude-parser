# Claude Parser - Offline Backlog System

## Overview
We now use **dstask** - a completely offline, git-backed task management system that Claude Code can manage autonomously. No cloud dependencies, no manual tracking needed.

## Key Features
- ✅ **100% Offline**: No internet required
- ✅ **Git-backed**: All tasks versioned in `~/.dstask`
- ✅ **Claude Code Driven**: Can be managed via CLI commands
- ✅ **Priority-based**: P0 (critical) to P3 (low)
- ✅ **Markdown notes**: Full documentation per task
- ✅ **Tag system**: Organize by feature areas

## Quick Commands for Claude Code

### View Tasks
```bash
# Show dashboard
python scripts/backlog_dashboard.py

# Show next priority tasks (JSON output)
dstask next

# Show all open tasks
dstask show-open

# Show active tasks
dstask show-active
```

### Manage Tasks
```bash
# Add new task
dstask add "Fix memory leak" project:claude-parser +bug P0

# Start working on task
dstask 2 start

# Complete task
dstask 2 done

# Add notes to task
dstask 2 note
# Then type/paste markdown notes

# Modify task
dstask 2 modify +urgent P0
```

### Git Sync
```bash
# Sync with git (if remote configured)
dstask sync

# Manual git operations
cd ~/.dstask
git add .
git commit -m "Updated tasks"
git push origin main  # If remote exists
```

## Priority Levels

- **P0 (Critical)**: Blocking issues, must fix immediately
  - Example: Files violating 150 LOC limit
  - Example: Broken tests

- **P1 (High)**: Important features needed soon
  - Example: WatcherManager for memory project
  - Example: Streaming for large files

- **P2 (Normal)**: Standard features and improvements
  - Example: Export functionality
  - Example: TypeScript SDK

- **P3 (Low)**: Nice-to-have, future considerations
  - Example: Visualizations
  - Example: Templates

## Current Task Summary

### P0 - Critical (Must Fix)
1. **Fix 5 files exceeding 150 LOC** (#2)
   - transcript_finder.py (265 lines)
   - jsonl_parser.py (242 lines)
   - message_repository.py (199 lines)
   - conversation_service.py (183 lines)
   - watcher.py (158 lines)

2. **Complete hook system verification** (#3)
   - PostToolUse hook testing
   - Integration verification

### P1 - High Priority
1. **WatcherManager implementation** (#4)
   - Non-blocking file monitoring
   - Status checking API
   - Backend auto-detection

2. **Streaming support** (#5)
   - Large JSONL file handling
   - Memory-efficient parsing

3. **AI context auto-update** (#6)
   - SessionStart hook
   - Auto-load CODEBASE_INVENTORY.json

### P2 - Normal Priority
- Export functionality (#7)
- Conversation diffing (#8)
- Token counting (#9)
- TypeScript SDK (#10)

### P3 - Low Priority
- Visualization (#11)
- Templates (#12)

## Automation Scripts

### `manage_backlog.py`
Full task management interface:
```bash
# Initialize backlog
python scripts/manage_backlog.py init

# Show status
python scripts/manage_backlog.py status

# Add task
python scripts/manage_backlog.py add "New feature"

# Complete task
python scripts/manage_backlog.py done 2
```

### `backlog_dashboard.py`
Visual dashboard:
```bash
# Show dashboard once
python scripts/backlog_dashboard.py

# Live update mode (refreshes every 5 seconds)
python scripts/backlog_dashboard.py watch
```

## Claude Code Workflow

### Starting a Session
```bash
# 1. Check current priorities
python scripts/backlog_dashboard.py

# 2. Pick highest priority task
dstask 2 start  # Start task #2

# 3. Work on task
# ... implement solution ...

# 4. Complete task
dstask 2 done

# 5. Check next task
dstask next
```

### Adding New Tasks
```bash
# Bug found
dstask add "Fix import error in hooks.py" project:claude-parser +bug P0

# Feature request
dstask add "Add CSV export" project:claude-parser +feature P2

# With detailed notes
dstask add "Refactor domain services" project:claude-parser +refactor P1
dstask 13 note  # Then add markdown notes
```

### Progress Tracking
```bash
# See what's in progress
dstask show-active

# See what was completed
dstask show-resolved

# Check specific tags
dstask show-open +bug
dstask show-open +feature
```

## Integration with Development

### Pre-commit Check
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Check for P0 tasks before committing
P0_COUNT=$(dstask next | grep -c '"P0"')
if [ $P0_COUNT -gt 0 ]; then
    echo "⚠️  Warning: $P0_COUNT critical tasks remain"
    dstask next | grep -A2 '"P0"'
fi
```

### CI/CD Integration
```yaml
# .github/workflows/check-tasks.yml
- name: Check Critical Tasks
  run: |
    dstask next | jq '[.[] | select(.priority == "P0")] | length' > p0_count
    if [ $(cat p0_count) -gt 0 ]; then
      echo "::warning::Critical tasks remain"
    fi
```

## Benefits Over Cloud Solutions

1. **Privacy**: Tasks never leave your machine
2. **Speed**: No network latency
3. **Reliability**: Works offline, always
4. **Version Control**: Full git history
5. **Scriptable**: CLI interface for automation
6. **Claude Code Native**: Perfect for AI-driven management

## Next Steps

1. **Immediate**: Fix the 5 files exceeding 150 LOC (task #2)
2. **Today**: Complete hook verification (task #3)
3. **This Week**: Implement WatcherManager (task #4)
4. **Future**: Work through P1/P2 tasks as needed

---

**Remember**: This backlog is now the single source of truth for tasks. No more scattered TODO comments or forgotten issues!