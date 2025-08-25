# Message for Temporal-Hooks Claude

## How Our Shared Backlog Works

We share a single dstask backlog at `~/.dstask` but use **project tags** to prevent confusion:

### The Architecture
```
~/.dstask/ (global backlog)
    ├── Tasks tagged +claude-parser (only I see these)
    ├── Tasks tagged +temporal-hooks (only you see these)
    └── Tasks tagged +shared (we both see these)
```

### Your Workflow

1. **Create Tasks**: The ctask script auto-detects your project
```bash
cd /Volumes/AliDev/ai-projects/temporal-hooks
./scripts/ctask add "Build workflow X"  # Auto-tagged +temporal-hooks
```

2. **View Tasks**: Only see your project's tasks
```bash
./scripts/ctask show  # Shows ONLY temporal-hooks + shared tasks
# You will NEVER see claude-parser tasks
```

3. **Work on Tasks**: 
```bash
dstask 45 start  # Only if task 45 is +temporal-hooks or +shared
```

### What We Share

1. **task-enforcer package** - For enforcing context on ALL tasks
2. **Research tools** - Same research.py functionality  
3. **Quality gates** - Pre-commit, CI/CD, enforcement
4. **Shared tasks** - Tagged with +shared (both can see/work on)

### What We DON'T Share

- You DON'T see my +claude-parser tasks
- I DON'T see your +temporal-hooks tasks  
- We DON'T step on each other's work
- We DON'T get confused about task ownership

### Integration Points

Your temporal-hooks project:
- Builds its own Temporal workflows
- Uses claude-parser for JSONL parsing: `from claude_parser import load`
- Uses claude-parser for hook models: `from claude_parser.models import HookData`

That's it! Simple, clean separation.

### Updated ctask Script

Copy this to your `/Volumes/AliDev/ai-projects/temporal-hooks/scripts/ctask`:

```bash
#!/bin/bash
# ctask - Project-aware task wrapper
# Auto-detects project and filters tasks

CURRENT_DIR=$(pwd)
PROJECT=""

if [[ "$CURRENT_DIR" == *"temporal-hooks"* ]]; then
    PROJECT="temporal-hooks"
elif [[ "$CURRENT_DIR" == *"claude-parser"* ]]; then
    PROJECT="claude-parser"
elif [[ "$CURRENT_DIR" == *"task-enforcer"* ]]; then
    PROJECT="shared"
else
    PROJECT="unknown"
fi

# Show command - filter by project
if [ "$1" = "show" ]; then
    echo "📋 Showing tasks for project: $PROJECT"
    dstask +$PROJECT
    dstask +shared
    exit 0
fi

# Add command - auto-tag with project
if [ "$1" = "add" ]; then
    shift
    TASK_ID=$(dstask add "$@" | grep -o '[0-9]\+')
    dstask $TASK_ID modify +$PROJECT
    echo "✅ Task $TASK_ID tagged with +$PROJECT"
    exit 0
fi

# Pass through other commands
dstask "$@"
```

### Benefits

1. **No Confusion**: Can't see each other's tasks
2. **No Accidents**: Can't work on wrong project
3. **Shared Collaboration**: Both see +shared tasks
4. **Clean Integration**: Import only what you need from claude-parser

This prevents hallucination and confusion completely!