# Claude Parser SDK - Capability Matrix

## Purpose
This matrix shows what the SDK can do, preventing duplicate implementations and ensuring correct usage.

## Core Capabilities

| Capability | Status | Location | Function/Class | Usage |
|------------|--------|----------|----------------|-------|
| **JSONL Parsing** | ✅ Complete | `claude_parser/__init__.py` | `load()` | `conversation = load("file.jsonl")` |
| **Message Extraction** | ✅ Complete | `models/message.py` | `Message` | Auto-parsed from JSONL |
| **Conversation Handling** | ✅ Complete | `models/conversation.py` | `Conversation` | Container for messages |
| **File Discovery** | ✅ Complete | `discovery/finder.py` | `find_files()` | Find all JSONL files |
| **Content Search** | ✅ Complete | `discovery/search.py` | `search_conversations()` | Search across files |
| **File Watching** | ✅ Complete | `watch/watcher.py` | `watch()` | Monitor for changes |
| **Hook Processing** | ✅ Complete | `hooks/` | Multiple functions | Claude Code integration |
| **Feature Tracking** | ✅ Complete | `features/registry.py` | `FeatureRegistry` | Track implementation status |

## Data Models

| Model | Purpose | Key Properties | Location |
|-------|---------|----------------|----------|
| `Message` | Single message entity | `role`, `content`, `timestamp` | `models/message.py` |
| `Conversation` | Message container | `messages`, `metadata` | `models/conversation.py` |
| `Event` | UI/System events | `type`, `data` | `models/event.py` |
| `Feature` | Feature definition | `name`, `status`, `category` | `features/models.py` |
| `FeatureStatus` | Implementation status | Enum: complete/partial/planned | `features/models.py` |

## Hook System Functions

| Function | Purpose | Returns | Example |
|----------|---------|---------|---------|
| `hook_input()` | Parse hook data | Dict | `data = hook_input()` |
| `exit_success()` | Success exit | Never | `exit_success()` |
| `exit_failure()` | Failure exit | Never | `exit_failure("error")` |
| `advanced.allow()` | Allow permission | Never | `advanced.allow("OK")` |
| `advanced.deny()` | Deny permission | Never | `advanced.deny("Blocked")` |
| `advanced.ask()` | Request user input | Never | `advanced.ask("Confirm?")` |

## File Operations

| Operation | Function | Location | Usage |
|-----------|----------|----------|-------|
| **Ensure exists** | `ensure_file_exists()` | `infrastructure/file_utils.py` | `path = ensure_file_exists(file)` |
| **Read JSONL** | `read_jsonl_file()` | `infrastructure/file_utils.py` | `lines = read_jsonl_file(path)` |
| **Parse JSON** | Built-in orjson | N/A | `orjson.loads(data)` |
| **Find files** | `find_files()` | `discovery/finder.py` | `files = find_files(directory)` |

## Search & Navigation

| Feature | Status | Function | Returns |
|---------|--------|----------|---------|
| Find by pattern | ✅ Complete | `Conversation.search()` | List[Message] |
| Filter by role | ✅ Complete | `Conversation.filter_by_role()` | List[Message] |
| Get by index | ✅ Complete | `Conversation[index]` | Message |
| Iterate messages | ✅ Complete | `for msg in conversation` | Message |
| Count messages | ✅ Complete | `len(conversation)` | int |

## Feature Categories

| Category | Description | Features | Status |
|----------|-------------|----------|--------|
| **Parser** | Core parsing | load, Message, Conversation | ✅ Complete |
| **Hooks** | Claude Code hooks | allow, deny, ask | ✅ Complete |
| **Watch** | File monitoring | watch, callbacks | ✅ Complete |
| **Transport** | Data transport | 🚧 Partial | In progress |
| **Navigation** | Message navigation | search, filter | ✅ Complete |
| **Discovery** | File discovery | find_files | ✅ Complete |

## Library Dependencies

| Need | Library Used | Alternative | Why |
|------|--------------|-------------|-----|
| JSON parsing | `orjson` | ❌ json | 3x faster |
| Date/time | `pendulum` | ❌ datetime | Better timezones |
| HTTP | `httpx` | ❌ requests | Async support |
| CLI | `typer` | ❌ argparse | Better UX |
| Validation | `pydantic` | ❌ manual | Auto validation |
| Functional | `toolz` | ❌ loops | Cleaner code |
| File watch | `watchfiles` | ❌ polling | Efficient |
| Retry | `tenacity` | ❌ try/except | Configurable |
| Logging | `loguru` | ❌ logging | Better output |
| Testing | `pytest` | ❌ unittest | Better fixtures |

## Common Tasks

### Load and search messages
```python
from claude_parser import load

conversation = load("file.jsonl")
results = conversation.search("error")
user_msgs = conversation.filter_by_role("user")
```

### Watch for changes
```python
from claude_parser.watch import watch

def callback(conv, new_messages):
    print(f"New messages: {len(new_messages)}")

watch("file.jsonl", callback)
```

### Hook integration
```python
from claude_parser.hooks import hook_input, advanced

data = hook_input()
if data["tool"] == "dangerous":
    advanced.deny("Not allowed")
else:
    advanced.allow("Approved")
```

### Feature checking
```python
from claude_parser.features import get_registry

registry = get_registry()
incomplete = registry.get_incomplete_features()
for feature in incomplete:
    print(f"{feature.name}: {feature.status}")
```

## What NOT to Implement

### ❌ Already Exists
- JSON parsing → Use `orjson`
- File validation → Use `ensure_file_exists()`
- Message parsing → Use `load()`
- Feature tracking → Use `FeatureRegistry`
- Hook formatting → Use `advanced` helpers
- File discovery → Use `find_files()`
- Retry logic → Use `tenacity`
- Date parsing → Use `pendulum`

### ❌ Against Principles
- Manual loops → Use `toolz`
- Custom validation → Use `pydantic`
- While True → Use `apscheduler`
- Raw JSON → Use `orjson`
- Manual CLI → Use `typer`
- Custom logging → Use `loguru`

## Status Legend
- ✅ **Complete**: Fully implemented, tested, documented
- 🚧 **Partial**: Basic implementation, needs completion
- 📋 **Planned**: Designed but not implemented
- ⭕ **Not Started**: Identified but no work done
- ⚠️ **Deprecated**: Will be removed

## Quick Decision Tree

```
Need to do X?
├── Is it JSON related? → Use orjson
├── Is it file related? → Check infrastructure/file_utils.py
├── Is it parsing JSONL? → Use load()
├── Is it a hook? → Check hooks/
├── Is it date/time? → Use pendulum
├── Is it HTTP? → Use httpx
├── Is it CLI? → Use typer
├── Is it validation? → Use pydantic
├── Is it iteration? → Use toolz
└── Doesn't exist? → Research a library first!
```

---

**Remember**: Every line of custom code is a failure to find the right library. Check this matrix before implementing anything!