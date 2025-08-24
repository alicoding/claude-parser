# Local Enforcement Setup (No GitHub Required)

## 1. Shell Aliases for Terminal Users

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Claude Parser development aliases
alias claude-start='cd /Users/ali/.claude/projects/claude-parser && python scripts/enforce_context.py'
alias claude-check='python scripts/check_inventory_sync.py && python scripts/verify_spec.py'
alias claude-update='python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json'

# Enforce context before any git operation
alias gst='python scripts/enforce_context.py && git status'
alias gco='python scripts/enforce_context.py && git checkout'
alias gcm='python scripts/enforce_context.py && git commit'
```

## 2. VS Code Task Runner

Create `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Claude: Load Context",
            "type": "shell",
            "command": "python",
            "args": ["scripts/enforce_context.py"],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": [],
            "runOptions": {
                "runOn": "folderOpen"
            }
        },
        {
            "label": "Claude: Update Inventory",
            "type": "shell",
            "command": "python",
            "args": ["scripts/codebase_inventory.py", ".", "--output", "docs/ai/CODEBASE_INVENTORY.json"],
            "group": "build",
            "presentation": {
                "reveal": "always"
            }
        }
    ]
}
```

## 3. Makefile Integration

Already exists! Just use:
```bash
make claude-context  # Check and update context
make precommit      # Runs all checks including context
```

## 4. Local Git Hooks (No GitHub)

Already installed:
- **Pre-commit**: Blocks commits if inventory is out of date
- **Post-merge**: Auto-updates inventory after pulling changes

## 5. Editor Startup Scripts

### For Cursor/VS Code
Create `.vscode/claude-startup.sh`:
```bash
#!/bin/bash
echo "🤖 Claude Code Context Check..."
python scripts/enforce_context.py
```

### For Vim/Neovim
Add to `.vimrc` or `init.vim`:
```vim
" Run context check when opening Python files in this project
autocmd VimEnter */claude-parser/*.py !python scripts/enforce_context.py
```

## 6. Watch Mode for Real-time Enforcement

Create `scripts/watch_context.py`:
```python
#!/usr/bin/env python3
"""Watch for file changes and remind about context."""

from pathlib import Path
import time
from watchfiles import watch

def on_change():
    print("\n⚠️  Files changed! Remember to check CAPABILITY_MATRIX.md")
    print("   Run: python scripts/check_inventory_sync.py")

if __name__ == "__main__":
    print("👀 Watching for changes...")
    for changes in watch('.'):
        on_change()
```

## 7. Terminal Prompt Integration

Add to your prompt (`.zshrc` or `.bashrc`):
```bash
# Show warning in prompt when in claude-parser directory
claude_context_prompt() {
    if [[ "$PWD" == *"claude-parser"* ]]; then
        echo "📚[AI-Context] "
    fi
}

# Add to your PS1/PROMPT
PS1='$(claude_context_prompt)'$PS1
```

## 8. Automated Reminders

Create a cron job or use `launchd` on macOS:
```bash
# Every 30 minutes, check if working in claude-parser
*/30 * * * * cd /Users/ali/.claude/projects/claude-parser && python scripts/check_inventory_sync.py
```

## Usage Workflow

1. **Start work session**: Run `claude-start` or `make claude-context`
2. **Before any code changes**: Context is automatically checked
3. **After pulling changes**: Inventory auto-updates (post-merge hook)
4. **Before committing**: Pre-commit hook validates everything

## Quick Commands

```bash
# Start a Claude session
python scripts/enforce_context.py

# Check if context is current
python scripts/check_inventory_sync.py

# Update context manually
python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json

# Full validation
make precommit
```

## Why This Works Without GitHub

1. **Local hooks** enforce rules at commit time
2. **Shell aliases** enforce at command time
3. **Editor integration** enforces at file open
4. **Make targets** provide easy commands
5. **Watch mode** provides real-time reminders

The key is **multiple touchpoints** - no matter how Claude Code is invoked, the context gets checked!