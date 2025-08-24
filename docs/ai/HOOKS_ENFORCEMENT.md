# Claude Code Hooks - Automatic Context Enforcement

## The IFTTT Pattern for Claude Code

Just like IFTTT (If This Then That), Claude Code hooks create automatic workflows:

- **If** Session Starts → **Then** Load Context
- **If** User Prompts About Implementation → **Then** Add Reminders  
- **If** Tool Creates New Code → **Then** Check for Duplicates
- **If** Tool Uses Forbidden Pattern → **Then** Block and Suggest Alternative

## Implementation

### 1. SessionStart Hook - Automatic Context Loading

**File**: `.claude/hooks/session_context.py`

Runs automatically when Claude Code:
- Starts a new session (`startup`)
- Resumes a session (`--resume`)
- Clears context (`/clear`)

**What it does**:
- Loads current codebase stats
- Injects AI context documentation paths
- Reminds about no memory between sessions
- Forces awareness of existing code

### 2. PreToolUse Hook - Guard Against Violations

**File**: `.claude/hooks/pretool_guard.py`

Runs before Write/Edit/MultiEdit tools execute.

**What it does**:
- Detects new class/function creation
- Checks for forbidden patterns (while True, import json, etc.)
- Asks for confirmation if creating new code
- Suggests checking CAPABILITY_MATRIX.md first

### 3. UserPromptSubmit Hook - Smart Context Addition

**File**: `.claude/hooks/prompt_context.py`

Runs when user submits any prompt.

**What it does**:
- Analyzes prompt for keywords (implement, fix, refactor)
- Adds relevant context based on intent
- Reminds about TDD for bug fixes
- Suggests checking existing implementations

## Configuration

**File**: `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [...],     // Auto-loads context
    "PreToolUse": [...],       // Guards against violations
    "UserPromptSubmit": [...]  // Adds smart reminders
  }
}
```

## How It Works

### Scenario 1: Starting New Session
```
User: Opens Claude Code
Hook: SessionStart fires
Result: Context automatically loaded
Claude: "I see this codebase has 85 classes..."
```

### Scenario 2: User Asks to Implement Feature
```
User: "Implement a caching system"
Hook: UserPromptSubmit analyzes "implement"
Result: Adds reminder to check CAPABILITY_MATRIX.md
Claude: Checks existing code before implementing
```

### Scenario 3: Claude Tries to Create Duplicate
```
Claude: Attempts to Write new parser class
Hook: PreToolUse detects "class Parser"
Result: Asks "Did you check if this already exists?"
Claude: Must confirm or check first
```

## Key Benefits

1. **Zero Manual Steps** - Hooks run automatically
2. **Context-Aware** - Analyzes actions and adds relevant info
3. **Fail-Safe** - Multiple enforcement points
4. **Non-Blocking** - Guides rather than blocks (mostly)
5. **Self-Documenting** - Explains why when intervening

## Testing the Hooks

### Test SessionStart
```bash
# Simulate session start
echo '{"hook_event_name":"SessionStart","source":"startup","session_id":"test","transcript_path":"test.jsonl","cwd":"."}' | python .claude/hooks/session_context.py
```

### Test PreToolUse
```bash
# Simulate creating new code
echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"claude_parser/new.py","content":"class NewClass:"}}' | python .claude/hooks/pretool_guard.py
```

### Test UserPromptSubmit
```bash
# Simulate implementation prompt
echo '{"hook_event_name":"UserPromptSubmit","prompt":"implement a new caching system"}' | python .claude/hooks/prompt_context.py
```

## Enforcement Layers

### Layer 1: Session Start (Proactive)
- Always loads context at session start
- No way to skip or forget
- Happens before any work begins

### Layer 2: Prompt Analysis (Reactive)
- Responds to user intent
- Adds targeted reminders
- Guides based on keywords

### Layer 3: Tool Guards (Protective)
- Last line of defense
- Catches violations before they happen
- Asks for confirmation

## Comparison: Before vs After Hooks

### Before Hooks
```
User: "Create a parser"
Claude: *Creates duplicate parser.py*
User: "We already have 3 parsers!"
Claude: "Sorry, I didn't know"
```

### After Hooks
```
User: "Create a parser"
UserPromptSubmit Hook: *Adds context about existing parsers*
Claude: "I see we already have parsers in models/parser.py..."
PreToolUse Hook: "Are you sure you want to create another?"
Claude: "Let me use the existing parser instead"
```

## Maintenance

The hooks are:
- **Self-contained** - Each hook is independent
- **Project-specific** - Use `$CLAUDE_PROJECT_DIR`
- **Version controlled** - Part of the project
- **Testable** - Can be run standalone

## Future Enhancements

Could add:
- **PostToolUse** - Log all changes for audit
- **Stop** - Summary of what was accomplished
- **Notification** - Alert on specific patterns
- **PreCompact** - Save important context before compacting

## Conclusion

With hooks, we've created an **autonomous enforcement system** that:
1. Works without user intervention
2. Adapts to user intent
3. Prevents violations before they happen
4. Maintains context across sessions

It's truly "If This Then That" for Claude Code - automatic, intelligent, and effective!