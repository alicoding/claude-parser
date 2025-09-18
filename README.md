# Claude Parser v2.1.0 🚀

[![PyPI version](https://badge.fury.io/py/claude-parser.svg)](https://badge.fury.io/py/claude-parser)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://alicoding.github.io/claude-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Git-like disaster recovery for Claude Code conversations**

Claude Parser treats every Claude API call as a git commit, enabling powerful recovery and analysis capabilities when things go wrong.

## 🎉 What's New in v2.1.0

### New Features
- **🔍 Export Domain** - Export conversations to different formats for indexing
- **📚 LlamaIndex Export** - `export_for_llamaindex()` for semantic search
- **🛠️ Fixed Discovery** - `discover_claude_files()` now properly returns file paths
- **📦 Complete API** - All filtering functions now properly exported

## 📋 v2.0.0 Major Changes
- **🎯 Complete API Redesign** - Clean, intuitive Python API with 30+ functions
- **📚 15 Domain Architecture** - Organized into focused, composable modules
- **🔧 CG Commands** - Full Git-like CLI for disaster recovery
- **🪝 CH Hook System** - Composable hooks for Claude Code integrations
- **📊 DuckDB Backend** - Efficient JSONL querying without intermediate storage
- **🏗️ LNCA Compliant** - Every file <80 LOC, 100% framework delegation
- **📖 Full Documentation** - Complete API reference, user guides, and examples

### Breaking Changes from v1
- New import structure: `from claude_parser import load_session` (not `from claude_parser.main`)
- Removed god objects - now uses focused domain modules
- All functions return plain dicts, not custom objects
- Pydantic schema normalization handles all JSONL variations

## 🚀 Quick Start

### Installation
```bash
pip install claude-parser
```

### Basic Usage

```python
from claude_parser import load_latest_session, analyze_session

# Load your most recent Claude session
session = load_latest_session()
print(f"Found session with {len(session['messages'])} messages")

# Analyze the session
analysis = analyze_session(session)
print(f"Total tokens: {analysis['total_tokens']}")
print(f"Estimated cost: ${analysis['estimated_cost']:.2f}")
```

### Disaster Recovery with CG Commands

```bash
# Oh no! Claude deleted important files!
python -m claude_parser.cli.cg find "important_file.py"

# Found it! Now restore it
python -m claude_parser.cli.cg checkout /path/to/important_file.py

# See what happened
python -m claude_parser.cli.cg reflog

# Jump back to before the disaster
python -m claude_parser.cli.cg reset abc123
```

## 🎯 Core Features

### Git-like Commands (CG)
- `cg status` - Current session state
- `cg log` - Conversation history
- `cg find <pattern>` - Search across all sessions
- `cg blame <file>` - Who last modified a file
- `cg checkout <file>` - Restore deleted files
- `cg reflog` - Operation history
- `cg show <uuid>` - Operation details
- `cg reset <uuid>` - Time travel to any point

### Composable Hooks (CH)
```bash
# Run hooks with custom executors
python -m claude_parser.cli.ch run --executor my_executor

# Or set default executor
export CLAUDE_HOOK_EXECUTOR=my_executor
```

### Python SDK

```python
from claude_parser import (
    # Session Management
    load_session, load_latest_session, discover_all_sessions,

    # Analytics
    analyze_session, analyze_tool_usage, analyze_token_usage,
    calculate_session_cost, calculate_context_window,

    # File Operations
    restore_file_content, generate_file_diff, compare_files,

    # Navigation
    find_message_by_uuid, get_message_sequence, get_timeline_summary,

    # Discovery
    discover_claude_files, discover_current_project_files,

    # Filtering (NEW in v2!)
    filter_messages_by_type, filter_messages_by_tool,
    search_messages_by_content, exclude_tool_operations,

    # Export (NEW in v2.1!)
    export_for_llamaindex  # Export conversations for semantic search
)
```

## 📊 Real-World Use Cases

### 1. Disaster Recovery
```python
from claude_parser import load_latest_session, restore_file_content

session = load_latest_session()
content = restore_file_content("/deleted/important.py", session)
with open("recovered.py", "w") as f:
    f.write(content)
```

### 2. Cost Analysis
```python
from claude_parser import load_latest_session, calculate_session_cost

session = load_latest_session()
cost = calculate_session_cost(
    input_tokens=100000,
    output_tokens=50000,
    model="claude-3-5-sonnet-20241022"
)
print(f"This session cost: ${cost['total_cost']:.2f}")
```

### 3. Message Filtering
```python
from claude_parser import load_latest_session, MessageType
from claude_parser.filtering import filter_messages_by_type

session = load_latest_session()
user_messages = filter_messages_by_type(session['messages'], MessageType.USER)
print(f"You sent {len(user_messages)} messages")
```

### 4. Real-time Monitoring
```python
from claude_parser.watch import watch

def on_assistant(message):
    print(f"Claude says: {message['content'][:100]}...")

watch("~/.claude/projects/current/session.jsonl", on_assistant=on_assistant)
```

### 5. Export for Semantic Search (NEW in v2.1!)
```python
from claude_parser import export_for_llamaindex

# Export conversations to LlamaIndex format
docs = export_for_llamaindex("session.jsonl")
# Returns: [{"text": "message", "metadata": {...}}, ...]

# Use with semantic search services
for doc in docs:
    print(f"Text: {doc['text'][:50]}...")
    print(f"Speaker: {doc['metadata']['speaker']}")
```

## 🏗️ Architecture

### Clean Domain Organization (19 modules)
```
claude_parser/
├── analytics/     # Session and tool analysis
├── api/           # API utilities
├── cli/           # CG and CH commands
├── core/          # Core utilities
├── discovery/     # File and project discovery
├── export/        # Export formats (NEW in v2.1!)
├── extensions/    # Extension system
├── filtering/     # Message filtering
├── hooks/         # Hook system and API
├── loaders/       # Session loading
├── messages/      # Message utilities
├── models/        # Data models
├── navigation/    # Timeline and UUID navigation
├── operations/    # File operations
├── queries/       # DuckDB SQL queries
├── session/       # Session management
├── storage/       # DuckDB engine
├── tokens/        # Token counting and billing
└── watch/         # Real-time monitoring
```

### LNCA Principles
- **<80 LOC per file** - Optimized for LLM comprehension
- **100% Framework Delegation** - No custom loops or error handling
- **Single Source of Truth** - One file per feature
- **Pydantic Everything** - Schema normalization for all JSONL variations

## 📖 Documentation

Full documentation available at: https://alicoding.github.io/claude-parser/

- [Getting Started Guide](https://alicoding.github.io/claude-parser/user-guide/getting-started/)
- [CLI Commands Reference](https://alicoding.github.io/claude-parser/cli/commands/)
- [API Reference](https://alicoding.github.io/claude-parser/api/complete-reference/)
- [Architecture Overview](https://alicoding.github.io/claude-parser/architecture/system-design/)

## 🔄 Migration from v1

### Old v1 Code
```python
# v1 - Complex imports, god objects
from claude_parser.main import ClaudeParser
parser = ClaudeParser()
parser.load_and_analyze_everything()  # God object doing too much
```

### New v2 Code
```python
# v2 - Clean, focused functions
from claude_parser import load_latest_session, analyze_session
session = load_latest_session()
analysis = analyze_session(session)  # One function, one purpose
```

### Key Differences
1. **No more god objects** - Each function does one thing well
2. **Plain dicts everywhere** - No custom classes to learn
3. **Explicit imports** - Import only what you need
4. **Better error handling** - Framework delegation (Pydantic/Typer)
5. **More features** - Filtering, watching, complete hook system

## 🚢 Deployment

### PyPI Release
```bash
# Build and upload to PyPI
python -m build
twine upload dist/*
```

### Documentation
Documentation auto-deploys to GitHub Pages on every push to main.

## 🗺️ Export Format Roadmap

### Currently Available (v2.1)
- ✅ **LlamaIndex** - `export_for_llamaindex()` - For semantic search indexing

### Planned Export Formats
- 🔜 **Mem0** - Long-term memory for AI agents
- 🔜 **ChromaDB** - Vector database format
- 🔜 **Pinecone** - Cloud vector database
- 🔜 **Markdown** - Human-readable conversation logs
- 🔜 **JSON-LD** - Structured data with context
- 🔜 **OpenAI Messages** - Direct OpenAI API format
- 🔜 **Anthropic Messages** - Direct Anthropic API format
- 🔜 **LangChain Documents** - LangChain document format
- 🔜 **Haystack Documents** - Haystack NLP framework

### Export Domain Architecture
```python
claude_parser/export/
├── __init__.py        # Export registry
├── llamaindex.py      # LlamaIndex format (DONE)
├── mem0.py           # Mem0 format (TODO)
├── chroma.py         # ChromaDB format (TODO)
├── markdown.py       # Markdown format (TODO)
└── ...               # More formats
```

## 🚀 Roadmap

### v3.0.0 - UI-Ready API (Coming Soon)
Complete redesign for zero-boilerplate UI development.

#### Core/Feature Layer Separation
- ✅ Audit complete - identified all internal vs public functions
- ✅ Framework delegation mapped (humanize, babel, arrow, rich)
- 🔜 `claude_parser.core` - Low-level utilities for advanced users
- 🔜 `claude_parser` - High-level UI-ready functions

#### Display-Ready Functions
```python
# Coming in v3.0.0
from claude_parser import (
    get_session_summary,         # "436 messages, 3 hours, $12.45"
    get_formatted_messages,       # Markdown-formatted conversation
    get_token_breakdown,          # "45,678 tokens ($12.45)"
    get_file_changes_display,     # Formatted diff with colors
    export_as_html,              # Complete HTML report
)

# One-liner, zero parsing needed:
print(get_session_summary(session))  # That's it!
```

#### Planned Features
- **Session Display**: Pre-formatted messages with timestamps, roles, emojis
- **Analytics Dashboard**: Human-readable metrics (not raw numbers)
- **File Operations**: Formatted diffs, file lists with status icons
- **Export Formats**: HTML, Markdown, JSON, PDF - all display-ready
- **Smart Defaults**: "No messages found" instead of empty arrays
- **Number Formatting**: "$12.45" not 0.01245, "45,678" not 45678
- **Time Formatting**: "2:34 PM" not timestamps, "3 hours ago" not seconds

#### Framework Delegation
All formatting delegated to specialized libraries:
- `humanize` - Number and size formatting
- `babel` - Currency formatting
- `arrow` - Time and date formatting
- `rich` - Terminal colors and tables
- `emoji` - Status indicators (✅ ❌ ⚠️)
- `tabulate` - Markdown/HTML tables
- `jinja2` - HTML report generation

### v2.2.0 - Bug Fixes (Next Release)
- ✅ Fixed token counting to match UI (v2.1.1)
- ✅ Fixed None message field handling
- 🔜 Additional message extraction improvements

## 🤝 Contributing

We welcome contributions! Please ensure:
- Files stay under 80 lines of code
- Use framework delegation (no custom loops)
- Add tests for new features
- Update documentation

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the Claude Code community
- Inspired by git's powerful recovery capabilities
- Designed with LNCA principles for LLM-native development

## 📊 Stats

- **19** specialized domains
- **35+** public functions
- **<80** lines per file
- **100%** framework delegation
- **0** custom error handling

---

**Ready to never lose code again?** Install v2.1.0 and experience the power of Git-like recovery for Claude Code!

```bash
pip install claude-parser==2.1.0
```

[Documentation](https://alicoding.github.io/claude-parser/) | [GitHub](https://github.com/alicoding/claude-parser) | [PyPI](https://pypi.org/project/claude-parser/)