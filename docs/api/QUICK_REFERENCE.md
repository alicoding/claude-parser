# Claude Parser SDK - Quick Reference

## 🚀 Installation

```bash
pip install claude-parser
```

## 📦 Current API Status

### ✅ Available Now

```python
# Parser Domain (Phase 1)
from claude_parser import load
conv = load("session.jsonl")

# Hooks Domain (Phase 2 - Partial)
from claude_parser.hooks import hook_input, HookData
data = hook_input()
conv = data.load_conversation()
```

### ✅ Available Now

```python
# Exit helpers (Phase 2 complete)
from claude_parser.hooks import exit_success, exit_block, exit_error

# Complete hook (3 lines)
data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

### ✅ Available Now - Watch with UUID Checkpoints

```python  
# Watch Domain with Native UUID Tracking (No byte positions!)
from claude_parser.watch import watch, watch_async

def on_new(conv, new_msgs):
    print(f"Got {len(new_msgs)} new messages")
    # Client tracks: last_uuid = new_msgs[-1].uuid

# Simple watching
watch("session.jsonl", on_new)

# Resume from UUID checkpoint
watch("session.jsonl", on_new, after_uuid="msg-123")

# Async with checkpoint
import asyncio
async def async_watch():
    async for conv, new_msgs in watch_async("session.jsonl", after_uuid="msg-456"):
        process(new_msgs)
        
asyncio.run(async_watch())
```

## 🎯 95% Use Cases

### Parse JSONL (1 line)
```python
conv = load("transcript.jsonl")
```

### Parse Hook Input (1 line)
```python
data = hook_input()
```

### Complete Hook (3 lines) ✅ Ready
```python
data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```

## 📊 Quick Stats

| Domain | Functions | Lines for 95% | Performance | Coverage |
|--------|-----------|---------------|-------------|----------|
| Parser | load() | 1 | < 200ms | 95% |
| Hooks | hook_input() | 1 | < 1ms | 100% |
| Hooks | exit_*() | 1 | < 1ms | 100% |
| Watch | watch() | 1 | < 100ms | 100% |
| Watch | watch_async() | 1 | < 100ms | 100% |
| Memory | MemoryExporter | 3 | < 10ms | 100% |
| UUID | Checkpoints | 1 | < 1ms | 100% |

## 🔍 Hook Types Reference

All 8 Claude Code hook types work with the same API:

| Hook Type | Key Fields | Use Case |
|-----------|------------|----------|
| PreToolUse | tool_name, tool_input | Block/allow tools |
| PostToolUse | tool_name, tool_response | React to results |
| UserPromptSubmit | prompt | Validate/enhance prompts |
| Stop | stop_hook_active | Continue processing |
| SubagentStop | stop_hook_active | Subagent control |
| Notification | message | Handle alerts |
| SessionStart | source | Load context |
| PreCompact | trigger, custom_instructions | Compaction control |

## 🛠️ Common Patterns

### Check Hook Type
```python
data = hook_input()
if data.hook_type == "PreToolUse":
    # Tool-specific logic
```

### Safe Field Access
```python
# Optional fields return None if not present
if data.tool_name:
    print(f"Tool: {data.tool_name}")

# Dict fields need safe access
file_path = data.tool_input.get("file_path", "") if data.tool_input else ""
```

### Load Conversation
```python
try:
    conv = data.load_conversation()
    errors = conv.with_errors()
except Exception as e:
    print(f"Could not load: {e}", file=sys.stderr)
```

## 🚫 Exit Codes

| Code | Meaning | Effect |
|------|---------|--------|
| 0 | Success | Continue normally |
| 1 | Error | Show error, continue |
| 2 | Block | Claude processes message |

## 📚 Full Documentation

- [Parser API](./parser.md)
- [Hooks API](./hooks.md)
- [Models](./models.md)
- [Changelog](./CHANGELOG.md)

## 🧪 Testing Your Hooks

```bash
# Test with echo (how Claude Code calls hooks)
echo '{"session_id":"test","transcript_path":"/test.jsonl","cwd":"/tmp","hook_event_name":"PreToolUse","tool_name":"Write"}' | python my_hook.py

# Check exit code
echo $?
```

## 💡 Tips

1. **Always use hook_input()** - Never parse stdin manually
2. **Check hook_type first** - Different hooks have different fields
3. **Handle missing fields** - Use `.get()` or check for None
4. **Use correct exit codes** - 0=success, 1=error, 2=block
5. **Write to stderr** - Claude only sees stderr on exit 2

## 🔄 Version

Current: **2.0.0** (Phase 2 complete - hooks + watch domains ready!)

Last Updated: 2024-08-20