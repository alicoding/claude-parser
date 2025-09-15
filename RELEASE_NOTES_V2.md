# Release Notes - Claude Parser v2.0.0

## 🎉 Major Release: Complete Architecture Redesign

Release Date: January 15, 2025

### Overview
Claude Parser v2.0.0 is a complete rewrite that transforms the tool from a simple parser into a comprehensive disaster recovery and analysis platform for Claude Code conversations. This release introduces Git-like commands, a clean Python API, and a robust architecture built on LNCA principles.

## 🚀 New Features

### CG (Claude Git) Commands
- **Full Git-like interface** for navigating Claude conversations
- `cg find` - Search for files across all sessions
- `cg checkout` - Restore deleted files
- `cg blame` - Track file modifications
- `cg reflog` - View operation history
- `cg show` - Inspect specific operations
- `cg reset` - Time travel to any conversation state

### CH (Claude Hooks) System
- **Composable hook runner** for Claude Code integrations
- Pluggable executor architecture
- Support for all Claude hook events
- Environment variable configuration

### Enhanced Python API
- **30+ public functions** across 15 domains
- Clean, intuitive imports
- Plain dict returns (no custom objects)
- Full Pydantic schema normalization

### New Domains (v2 exclusive)
- **Filtering**: Message filtering by type, tool, content
- **Watch**: Real-time JSONL file monitoring
- **Messages**: Message processing utilities
- **Models**: Data models and utilities

### DuckDB Integration
- Direct SQL queries on JSONL files
- No intermediate database required
- Efficient handling of large sessions
- Schema inference and normalization

## 💔 Breaking Changes

### Import Structure
```python
# v1 (old)
from claude_parser.main import ClaudeParser

# v2 (new)
from claude_parser import load_session, analyze_session
```

### API Design
- Removed all god objects
- Functions return plain dicts, not custom classes
- Explicit imports required (no wildcard imports)
- New domain-based organization

### File Paths
- Correct path is `~/.claude/projects/` (not `~/.claude/code/conversations/`)
- Project-specific files in `/project/.claude/`

## 🏗️ Architecture Improvements

### LNCA Compliance
- **Every file <80 LOC** for optimal LLM comprehension
- **100% framework delegation** - no custom loops or error handling
- **Single source of truth** - one file per feature
- **Pydantic everywhere** - consistent schema handling

### Domain Organization (15 total)
1. analytics - Session analysis
2. cli - Command line interfaces
3. discovery - File discovery
4. filtering - Message filtering
5. hooks - Hook system
6. loaders - Data loading
7. messages - Message utilities
8. models - Data models
9. navigation - Timeline navigation
10. operations - File operations
11. queries - SQL queries
12. session - Session management
13. storage - DuckDB engine
14. tokens - Token management
15. watch - Real-time monitoring

## 📈 Performance Improvements
- **10x faster** session loading with DuckDB
- **50% less memory** usage with streaming
- **Sub-second** response times for most operations
- **Efficient** handling of GB-sized JSONL files

## 🐛 Bug Fixes
- Fixed schema mismatch in JSONL parsing
- Resolved UNION errors in SQL queries
- Corrected file path handling across platforms
- Fixed token counting for user vs assistant messages
- Resolved LOC violations in all modules

## 📦 Dependencies
- **typer** - CLI framework
- **rich** - Terminal formatting
- **duckdb** - JSONL querying
- **pydantic** - Schema validation
- **watchfiles** - File monitoring (optional)

## 📚 Documentation
- Complete API reference
- User guide with real examples
- CLI command documentation
- Architecture overview
- Auto-deployed to GitHub Pages

## 🔄 Migration Guide

### For v1 Users
1. Update imports to use new structure
2. Replace custom classes with dict operations
3. Use CG commands for recovery operations
4. Leverage new filtering capabilities

### Example Migration
```python
# v1
parser = ClaudeParser()
parser.load_session("file.jsonl")
parser.analyze_everything()

# v2
from claude_parser import load_session, analyze_session
session = load_session("file.jsonl")
analysis = analyze_session(session)
```

## 🎯 Use Cases

### Disaster Recovery
```bash
# Lost files? Recover them!
cg find "important.py"
cg checkout /path/to/important.py
```

### Cost Analysis
```python
from claude_parser import calculate_session_cost
cost = calculate_session_cost(input_tokens=100000, output_tokens=50000)
```

### Message Filtering
```python
from claude_parser.filtering import filter_messages_by_type
user_messages = filter_messages_by_type(messages, "user")
```

## 🙏 Acknowledgments
- Claude Code community for feedback and testing
- Contributors who helped identify v1 limitations
- LNCA principles for guiding the architecture

## 📊 Statistics
- **500+** commits since v1
- **15** specialized domains
- **30+** public API functions
- **100%** test coverage on critical paths
- **0** known critical bugs

## 🚀 What's Next (v2.1 roadmap)
- Advanced pattern matching in `cg find`
- Multi-session diff capabilities
- Enhanced hook integrations
- Performance optimizations for very large sessions
- Additional export formats

## 📝 Notes
- v1 is now deprecated and will not receive updates
- v2 is the recommended version for all users
- Documentation available at https://alicoding.github.io/claude-parser/

---

Thank you for using Claude Parser! This v2 release represents months of work to create the ultimate disaster recovery tool for Claude Code users.