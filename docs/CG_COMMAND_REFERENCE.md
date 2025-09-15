# CG Commands Reference
**Claude Git-like Interface for Session History**

CG provides git-like commands to navigate and restore Claude conversation history. Each API call creates a "commit" with UUID tracking.

## ✅ Working Commands

### Basic Commands
- `cg status` - Show current session status
- `cg log` - Show conversation history (like git log)

### Advanced Commands (Fixed 2025-01-14)
- `cg find <pattern>` - Find files matching pattern across all sessions
- `cg blame <full-file-path>` - Show who last modified a file
- `cg reflog` - Show all operations history
- `cg show <uuid>` - Show details of specific operation
- `cg checkout <uuid>` - Restore to specific state (partial implementation)

## Usage Examples

### Find Operations
```bash
# Find all operations on test files
python -m claude_parser.cli.cg find "test_"

# Find specific file operations
python -m claude_parser.cli.cg find "discovery/core.py"
```

### Blame Operations
```bash
# Show last modification (requires full path)
python -m claude_parser.cli.cg blame "/Volumes/AliDev/ai-projects/claude-parser/test_cg_demo.py"
```

### History Operations
```bash
# Show recent operations
python -m claude_parser.cli.cg reflog

# Show specific operation details
python -m claude_parser.cli.cg show af03b2e2
```

## Technical Implementation

### Architecture
- **Storage**: DuckDB queries on JSONL files
- **Schema**: Pydantic models for normalization (`schema_models.py`)
- **Queries**: Separated modules (`find_queries.py`, `blame_queries.py`, `reflog_queries.py`)
- **CLI**: Split across multiple files for LOC compliance

### Schema Handling
Uses Pydantic models to handle JSONL schema variations:
- `toolUseResult` can be string or dict - auto-normalized
- Consistent interface via `NormalizedMessage` model
- Framework delegation instead of custom parsing

### Fixed Issues (2025-01-14)
1. **Schema mismatch**: Fixed queries to use `toolUseResult.filePath` instead of `tool_input.file_path`
2. **UNION errors**: Replaced with `query_all_jsonl()` utility
3. **LOC violations**: Split large files into focused modules
4. **Custom code**: Replaced manual JSON parsing with Pydantic

## File Locations
- Main CLI: `claude_parser/cli/cg.py`
- Advanced commands: `claude_parser/cli/cg_advanced.py`, `claude_parser/cli/cg_reflog.py`
- Query modules: `claude_parser/queries/`
- Schema models: `claude_parser/queries/schema_models.py`

## Known Limitations
- `cg blame` requires full file paths
- `cg checkout` is partially implemented
- Schema assumes Claude Code JSONL format

## Future Enhancements
- Full git-like checkout/reset functionality
- Better path resolution for blame
- Integration with `ch` hooks system