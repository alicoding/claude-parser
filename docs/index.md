# Claude Parser

**Git-like interface for Claude Code disaster recovery**

## What is Claude Parser?

Claude Parser provides `cg` (Claude Git) commands that treat every Claude API call as a git commit, allowing you to:

- 🔍 **Find lost code** - Search across all Claude sessions
- ⏰ **Restore deleted files** - Recover from any point in history
- 🚀 **Navigate by UUID** - Jump to any conversation state
- 💾 **Zero tokens** - All operations work locally on JSONL files

## Quick Start

```bash
# Install
pip install claude-parser

# Find lost test files
cg find "test_"

# Restore a deleted file
cg checkout myfile.py

# Show what happened at a specific point
cg show <uuid>

# View operation history
cg reflog
```

## Why Claude Parser?

Every Claude Code interaction is saved as JSONL. When disaster strikes:

- **"Claude deleted my files!"** → `cg find` + `cg checkout`
- **"Lost context between sessions"** → `cg reflog` + `cg show`
- **"Need previous version"** → `cg blame` + `cg checkout`

## Core Features

### 🎯 CG Commands
- `cg status` - Current session state
- `cg log` - Message history
- `cg find <pattern>` - Search all sessions
- `cg blame <file>` - Last modifier
- `cg checkout <file>` - Restore file
- `cg reset <uuid>` - Reset to state
- `cg show <uuid>` - Show operation details

### 🔧 Architecture
- **DuckDB** queries on JSONL files
- **Pydantic** schema normalization
- **<80 LOC** per file (LNCA compliant)
- **Framework delegation** - no custom loops

## Getting Started

See the [User Guide](user-guide/disaster-recovery.md) for common disaster recovery scenarios.