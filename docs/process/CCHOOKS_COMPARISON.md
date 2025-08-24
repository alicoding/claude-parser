# Claude Parser SDK vs cchooks: Feature Comparison

## Critical Features We MUST Match or Exceed

### ✅ Features We're Improving

| Feature | cchooks | Claude Parser SDK | Improvement |
|---------|---------|-------------------|-------------|
| **Basic Usage** | 15+ lines with try/catch | 3 lines | **80% reduction** |
| **Type Checking** | `isinstance()` required | Not needed | **Simpler** |
| **Context Creation** | Factory pattern | Direct function | **Less complexity** |
| **Import Complexity** | Multiple imports | Single import | **Cleaner** |
| **Error Handling** | Manual try/catch | Built-in | **Automatic** |

### ⚠️ Features We Must Ensure Parity

#### 1. Hook-Specific Output Methods
**cchooks provides:**
- PreToolUse: `allow()`, `deny()`, `ask()`, `halt()`
- PostToolUse: `accept()`, `challenge()`, `ignore()`, `halt()`
- UserPromptSubmit: `allow()`, `block()`, `add_context()`
- Stop/SubagentStop: `allow()`, `prevent()`
- SessionStart: `additional_context()`

**Our Solution:**
```python
# 95% use simple exits
exit_success()  # Covers allow/accept/acknowledge
exit_block("reason")  # Covers deny/block/prevent

# 5% use advanced methods (when needed)
from claude_parser.hooks import hook_input, advanced

data = hook_input()

# Hook-specific convenience methods (optional)
if data.hook_type == "PreToolUse":
    advanced.deny("reason")  # Generates correct JSON
    advanced.ask()  # Asks user
    
if data.hook_type == "UserPromptSubmit":
    advanced.add_context("extra context")
```

#### 2. JSON Output Control
**cchooks provides:**
- Automatic JSON formatting for each hook type
- Handles deprecated fields
- `suppressOutput` support

**Our Solution Must Include:**
```python
def json_output(decision=None, reason=None, **kwargs):
    """Smart JSON output matching Claude's expectations."""
    data = hook_input()  # Get context
    
    # Auto-detect format based on hook type
    if data.hook_type == "PreToolUse":
        output = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason
            }
        }
    elif data.hook_type == "UserPromptSubmit" and "context" in kwargs:
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": kwargs["context"]
            }
        }
    else:
        output = {"decision": decision, "reason": reason}
    
    # Add common fields
    if "suppress_output" in kwargs:
        output["suppressOutput"] = kwargs["suppress_output"]
    
    print(orjson.dumps(output).decode())
    sys.exit(0)
```

#### 3. Error Handling
**cchooks provides:**
- `safe_create_context()` with automatic error handling
- Specific exception types
- Error handlers for each error type

**Our Solution:**
```python
def hook_input():
    """Automatically handles all errors."""
    try:
        data = orjson.loads(sys.stdin.read())
        return HookData(**data)
    except orjson.JSONDecodeError:
        print("Error: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: Missing required fields: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

#### 4. Type Safety
**cchooks provides:**
- Literal types for tools, decisions, triggers
- Type hints throughout

**Our Solution:**
```python
from typing import Literal, Optional

ToolName = Literal["Task", "Bash", "Glob", "Grep", "Read", 
                   "Edit", "MultiEdit", "Write", "WebFetch", "WebSearch"]
HookType = Literal["PreToolUse", "PostToolUse", "Notification",
                   "UserPromptSubmit", "Stop", "SubagentStop", 
                   "PreCompact", "SessionStart"]

class HookData(BaseModel):
    hook_event_name: HookType
    tool_name: Optional[ToolName] = None
    # ... rest of fields
```

#### 5. Utility Functions
**cchooks provides:**
- `read_json_from_stdin()`
- `validate_required_fields()`
- Safe accessors (`safe_get_str`, etc.)

**Our Solution (95/5 principle):**
```python
# 95% don't need these - hook_input() handles everything
data = hook_input()  # Validation automatic

# 5% advanced users can access internals if needed
from claude_parser.hooks.utils import safe_get

value = safe_get(data.tool_input, "file_path", default="")
```

## Features We're Adding (Not in cchooks)

### 1. Conversation Loading
```python
data = hook_input()
conv = data.load_conversation()  # Full Claude Parser SDK power
recent_errors = conv.with_errors()
```

### 2. Simpler API
```python
# cchooks - complex
from cchooks import create_context
from cchooks.contexts import PreToolUseContext

try:
    context = create_context()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)

if isinstance(context, PreToolUseContext):
    if context.tool_name == "Write":
        context.output.deny("No writes")

# Claude Parser SDK - simple
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

### 3. True 95/5 Design
- 95% users: 3 functions (`hook_input`, `exit_success`, `exit_block`)
- 5% users: Advanced features available but not required

## Migration Guide from cchooks

### Basic Hook
```python
# Before (cchooks)
from cchooks import create_context
from cchooks.contexts import PreToolUseContext

def main():
    try:
        context = create_context()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if isinstance(context, PreToolUseContext):
        if context.tool_name == "Write":
            context.output.deny("No writes")
        else:
            context.output.allow()

# After (Claude Parser SDK)
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if data.tool_name == "Write": 
    exit_block("No writes")
exit_success()
```

### Advanced JSON Output
```python
# Before (cchooks)
context.output.deny("Reason", suppress_output=True)

# After (Claude Parser SDK)
from claude_parser.hooks import json_output
json_output(decision="deny", reason="Reason", suppress_output=True)
```

## Ensuring No Downgrades

### ✅ We Match All Core Functionality
- [x] All 8 hook types supported
- [x] JSON output with correct formatting
- [x] Exit code handling
- [x] Error handling
- [x] Type safety

### ✅ We Improve the Experience
- [x] 80% less code for basic hooks
- [x] No isinstance() checks needed
- [x] No factory pattern complexity
- [x] Built-in conversation loading
- [x] Automatic error handling

### ✅ We Maintain Compatibility
- [x] All field names match official API
- [x] JSON output formats correct
- [x] Exit codes work as expected
- [x] Can handle all edge cases

## Conclusion

Our Claude Parser SDK is a **strict upgrade** over cchooks:
- **Simpler**: 3 lines vs 15+ lines
- **More Powerful**: Conversation access built-in
- **No Downgrades**: All features matched or exceeded
- **95/5 Compliant**: Simple by default, powerful when needed