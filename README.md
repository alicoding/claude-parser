# Claude Parser SDK

[![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen)](https://github.com/anthropics/claude-parser)
[![Tests](https://img.shields.io/badge/tests-177%20passing-brightgreen)](https://github.com/anthropics/claude-parser)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

Professional Python SDK for parsing Claude Code JSONL conversation exports with full type safety and enterprise-grade architecture.

## Features

- **🚀 Simple API** - One line to parse conversations: `conv = load("session.jsonl")`
- **🏗️ Enterprise Architecture** - Domain-Driven Design with clean separation of concerns
- **⚡ High Performance** - orjson for 10x faster parsing, pydantic v2 for validation
- **🔍 Rich Queries** - Search, filter, and analyze conversations with ease
- **📱 Real-time** - Watch files for live conversation updates with UUID checkpoints
- **🎯 Type Safe** - Full type hints and validation throughout
- **🔄 UUID Checkpoints** - Native Anthropic UUID tracking, no byte positions
- **📊 Memory Export** - Export conversations for LlamaIndex/semantic search
- **🧪 Well Tested** - 84% coverage with 390+ passing tests

## Quick Start

```bash
pip install claude-parser
```

### CLI Usage

```bash
# Parse a JSONL file
claude-parser parse conversation.jsonl

# Parse with detailed statistics
claude-parser parse conversation.jsonl --stats

# Find current Claude transcript
claude-parser find

# List all Claude projects
claude-parser projects

# Export for semantic search (outputs JSON lines)
claude-parser export conversation.jsonl > memories.jsonl
claude-parser export conversation.jsonl --no-tools  # Exclude tool messages

# Watch file for live updates
claude-parser watch conversation.jsonl

# Resume watching from UUID checkpoint
claude-parser watch conversation.jsonl --after-uuid msg-123
```

### Python SDK Usage

```python
from claude_parser import load

# Load any Claude Code JSONL export
conv = load("conversation.jsonl")

# Access messages with full typing
print(f"Total messages: {len(conv.messages)}")
print(f"Assistant messages: {len(conv.assistant_messages)}")
print(f"User messages: {len(conv.user_messages)}")

# Search and filter
errors = conv.search("error")
recent = conv.before_summary(limit=10)

# Rich domain operations
for msg in conv.assistant_messages:
    print(f"{msg.timestamp}: {msg.text_content[:100]}...")
```

## Enterprise Features

### Domain-Driven Design Architecture

```python
from claude_parser.application import ConversationService
from claude_parser.domain import ConversationAnalyzer

# Application layer for complex operations
service = ConversationService()
conv = service.load_conversation("session.jsonl")

# Domain services for analysis
analyzer = ConversationAnalyzer(conv)
stats = analyzer.get_stats()
```

### Real-time File Watching with UUID Checkpoints

```python
from claude_parser.watch import watch, watch_async

def on_new_messages(conv, new_messages):
    print(f"Received {len(new_messages)} new messages")
    # Track checkpoint: last_uuid = new_messages[-1].uuid
    
# Watch for live updates
watch("session.jsonl", on_new_messages)

# Resume from UUID checkpoint (no byte positions!)
watch("session.jsonl", on_new_messages, after_uuid="msg-123")

# Async watching with checkpoint
import asyncio
async def watch_with_checkpoint():
    async for conv, new_messages in watch_async("session.jsonl", after_uuid="msg-456"):
        print(f"New: {len(new_messages)}")
        
asyncio.run(watch_with_checkpoint())
```

### Memory Export for Semantic Search

```python
from claude_parser.memory import MemoryExporter

# Export conversations as simple dicts for LlamaIndex
exporter = MemoryExporter(exclude_tools=True)

# Single conversation
conv = load("session.jsonl")
memories = exporter.export_as_dicts(conv)
# Returns: [{"text": "...", "metadata": {...}}, ...]

# Entire project (generator for efficiency)
for memory_dict in exporter.export_project("/path/to/project"):
    # Each dict ready for LlamaIndex Document creation
    semantic_search.index(memory_dict)
```

### Discovery and Navigation

```python
from claude_parser.discovery import find_current_transcript, list_all_projects

# Auto-discover transcripts
transcript = find_current_transcript()
if transcript:
    conv = load(transcript)

# List all available projects
projects = list_all_projects()
```

## Documentation

- **[API Reference](docs/api/)** - Complete API documentation
- **[Watch API with UUID Checkpoints](docs/api/watch-uuid-api.md)** - Real-time watching with resume support
- **[Memory Export API](docs/api/memory-export-api.md)** - Export for LlamaIndex/semantic search
- **[DDD Architecture](docs/api/ddd-architecture.md)** - Enterprise architecture overview
- **[Quick Reference](docs/api/QUICK_REFERENCE.md)** - Common patterns and examples

## Installation

### Requirements

- Python 3.11+
- See [pyproject.toml](pyproject.toml) for dependencies

### Development Setup

```bash
git clone https://github.com/anthropics/claude-parser
cd claude-parser
poetry install
poetry run pytest

# Run the CLI
poetry run claude-parser --help
```

## Architecture

Claude Parser follows Domain-Driven Design principles:

- **Domain Layer** - Core business logic and entities
- **Infrastructure Layer** - Data access with Repository pattern  
- **Application Layer** - Use cases and orchestration

This ensures maintainability, testability, and extensibility for enterprise use.

## Performance

- **10x faster JSON parsing** with orjson
- **Type-safe validation** with pydantic v2
- **Memory efficient** streaming for large files
- **O(1) message lookups** with built-in indexing

## Contributing

1. Read [CLAUDE.md](CLAUDE.md) for development rules
2. Follow DDD architecture patterns
3. Maintain 90%+ test coverage
4. Use conventional commits

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Enterprise Support**: This project follows enterprise-grade development practices with comprehensive testing, documentation, and clean architecture.