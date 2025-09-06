# Handoff Message for Temporal-Hooks Claude

## Context
We've simplified the collaboration between claude-parser and temporal-hooks projects. Both projects share the same dstask backlog at ~/.dstask but use project tags to prevent confusion.

## What You Need to Know

### 1. Task Management
Every task MUST have a project tag:
```bash
# Your tasks
dstask add "Create workflow" +temporal-hooks

# Shared tasks
dstask add "Update task-enforcer" +shared

# View only your tasks
dstask +temporal-hooks
dstask +shared
```

### 2. Updated ctask Script
The ctask wrapper now auto-detects project:
```bash
# In temporal-hooks directory
ctask add "Build workflow"  # Automatically tagged +temporal-hooks
ctask show                   # Shows only temporal-hooks + shared tasks
```

### 3. Our Integration Points
- **You provide**: Temporal workflows for complex task orchestration
- **We provide**: JSONL parsing and hook support for your workflow events
- **Shared**: task-enforcer package (enforces context, prevents violations)

### 4. No Direct Code Dependencies
- You build your own workflows
- We parse JSONL and trigger hooks
- Communication happens through:
  - JSONL event streams
  - Hook triggers
  - Shared task management

### 5. Task Enforcer Package
Located at: /Volumes/AliDev/ai-projects/task-enforcer/
- Enforces task context (RESEARCH, DUPLICATES, COMPLEXITY, SUCCESS CRITERIA)
- Prevents cross-project task confusion
- Auto-generates 1500+ chars of context
- Blocks tasks without proper documentation

## Your Action Items

1. **Update your CLAUDE.md** with:
```markdown
# Task Filtering Rules
- ALWAYS use: dstask +temporal-hooks
- NEVER use plain dstask without filter
- Shared tasks: dstask +shared
```

2. **Use ctask for all task operations**:
```bash
ctask add "description"  # Creates enforced task
ctask show              # Shows filtered tasks
ctask start <id>        # Validates before starting
```

3. **Follow the enforcement**:
- Every task needs full context
- Run `python scripts/research.py` before implementing
- Check for duplicates with grep
- Analyze complexity with radon

## Benefits
- No confusion about which tasks belong to which project
- Can't accidentally work on wrong project's tasks
- Shared tasks visible to both projects
- Full context prevents hallucination
- Enforced quality standards

## Questions?
The ctask script and task-enforcer package handle all the complexity. Just use ctask instead of dstask and everything works automatically.
