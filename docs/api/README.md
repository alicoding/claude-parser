# Claude Parser SDK - API Documentation

## 📚 Documentation Structure (DDD)

The API documentation is organized by **bounded contexts** following Domain-Driven Design:

### Core Domains
- **[Parser Domain](./parser.md)** - JSONL parsing and conversation loading ✅
- **[Hooks Domain](./hooks.md)** - Claude Code hook helpers (Phase 2) ✅ 
- **[Watch Domain](./watch.md)** - File monitoring and real-time updates (Phase 2) ✅

### Quick Links
- **[Quick Reference](./QUICK_REFERENCE.md)** - One-page cheat sheet 🚀
- **[Changelog](./CHANGELOG.md)** - What's new and changed 📝

### Supporting Domains
- **[Models](./models.md)** - Data models and types
- **[Analytics Domain](./analytics.md)** - Conversation analysis (Future)
- **[Memory Domain](./memory.md)** - Memory system integration (Future)

### Infrastructure
- **[Error Handling](./errors.md)** - Exception handling and recovery
- **[Performance](./performance.md)** - Benchmarks and optimization

---

## 🚀 Quick Start (95% Use Case)

### Parser - Load Conversations
```python
from claude_parser import load

conv = load("session.jsonl")
print(f"📊 {len(conv)} messages")
```
[Full Parser API →](./parser.md)

### Hooks - Handle Claude Events
```python
from claude_parser.hooks import hook_input, exit_block, exit_success

data = hook_input()
if data.tool_name == "Write": exit_block("No writes")
exit_success()
```
[Full Hooks API →](./hooks.md)

### Watch - Monitor Files ✅ Ready
```python
from claude_parser.watch import watch

def on_new(conv, messages):
    print(f"Got {len(messages)} new messages")

watch("transcript.jsonl", on_new)
```
[Full Watch API →](./watch.md)

---

## 📖 API Design Principles

### 95/5 Principle
- **95% of users**: Need only 1-3 lines of code
- **5% of users**: Get full power through advanced APIs

### Domain-Driven Design
- Each domain has clear boundaries
- No cross-domain dependencies
- Models are immutable value objects
- Services handle domain logic

### Library-First
- Uses best-in-class libraries (orjson, pydantic, watchfiles)
- No custom implementations where libraries exist
- Performance through proven solutions

---

## 🔍 Finding What You Need

| I want to... | Go to... |
|-------------|----------|
| Load and parse JSONL files | [Parser Domain](./parser.md) |
| Handle Claude Code hooks | [Hooks Domain](./hooks.md) |
| Monitor files for changes | [Watch Domain](./watch.md) |
| Understand message types | [Models](./models.md) |
| Handle errors gracefully | [Error Handling](./errors.md) |
| Optimize performance | [Performance](./performance.md) |

---

## 📦 Installation

```bash
pip install claude-parser
```

### Optional Features
```bash
# For file watching
pip install claude-parser[watch]

# For analytics (future)
pip install claude-parser[analytics]

# All features
pip install claude-parser[all]
```

---

## 🎯 Version Compatibility

- **Python**: 3.10+
- **Claude Code**: All export formats (2024-2025)
- **Pydantic**: v2.0+
- **Type hints**: Full support

---

## 📚 Complete Example

```python
from claude_parser import load
from claude_parser.hooks import hook_input, exit_success
from claude_parser.watch import watch

# 1. Parse conversations
conv = load("session.jsonl")
errors = conv.with_errors()
print(f"Found {len(errors)} errors")

# 2. Handle hooks
data = hook_input()
if data.hook_type == "PreToolUse":
    # Access conversation from hook
    conv = data.load_conversation()
    recent = conv.before_summary(10)
    exit_success()

# 3. Monitor changes
def process_new(conv, new_messages):
    for msg in new_messages:
        print(f"New: {msg.type}")

watch("live_session.jsonl", process_new)
```

---

## 📞 Support

- GitHub: [claude-parser/issues](https://github.com/your-org/claude-parser)
- Docs: [claude-parser.readthedocs.io](https://claude-parser.readthedocs.io)

## 📄 License

MIT License - see LICENSE file