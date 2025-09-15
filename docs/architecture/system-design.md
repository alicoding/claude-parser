# Claude Parser Architecture

## System Overview

Claude Parser is a disaster recovery and analysis tool for Claude Code conversations. It treats every Claude API call as a "git commit" with a UUID, enabling Git-like navigation through conversation history.

## Core Design Principles

### LNCA (LLM-Native Composable Architecture)
- **<80 LOC per file**: Every module stays under 80 lines for optimal LLM context
- **100% Framework Delegation**: No custom loops, error handling, or data processing
- **Single Source of Truth**: One file per feature, no duplication
- **Pydantic Schema Normalization**: All JSONL variations handled by Pydantic models

## Architecture Layers

```
┌─────────────────────────────────────────┐
│          CLI Layer (cg commands)        │
├─────────────────────────────────────────┤
│         Python API (SDK functions)      │
├─────────────────────────────────────────┤
│     Core Modules (Business Logic)       │
├─────────────────────────────────────────┤
│    Storage Layer (DuckDB + JSONL)       │
└─────────────────────────────────────────┘
```

## Module Organization

### `/claude_parser/cli/`
Git-like command interface, split for LOC compliance:
- `cg.py` - Main orchestrator (34 lines)
- `cg_basic.py` - Status, log commands (67 lines)
- `cg_advanced.py` - Find, blame commands (69 lines)
- `cg_reflog.py` - Reflog, show commands (80 lines)
- `cg_restore.py` - Checkout, restore commands (61 lines)
- `cg_reset.py` - Reset commands (63 lines)

### `/claude_parser/loaders/`
Data loading with framework delegation:
- `session.py` - Session loading via JSON (52 lines)
- `discovery.py` - File discovery via pathlib (73 lines)

### `/claude_parser/queries/`
DuckDB queries, one file per feature:
- `session_queries.py` - Session SQL queries
- `find_queries.py` - Find operations
- `blame_queries.py` - Blame operations
- `reflog_queries.py` - Reflog history
- `schema_models.py` - Pydantic normalization

### `/claude_parser/operations/`
File operations, split by responsibility:
- `core.py` - Re-exports for compatibility (20 lines)
- `file_ops.py` - File operations (42 lines)
- `diff_ops.py` - Diff generation (35 lines)
- `restore_ops.py` - Restoration logic (79 lines)

### `/claude_parser/navigation/`
Message navigation and timeline:
- `core.py` - Message filtering
- `timeline.py` - UUID time travel
- `checkpoint.py` - Recovery point detection

### `/claude_parser/tokens/`
Token counting and billing:
- `core.py` - Token operations
- `context.py` - Context window calculation
- `billing.py` - Cost estimation

### `/claude_parser/analytics/`
Session analysis:
- `core.py` - Core analytics
- `tools.py` - Tool usage analysis
- `projects.py` - Project context analysis

### `/claude_parser/hooks/`
Claude Code hook system:
- `request.py` - Hook request model
- `aggregator.py` - Response aggregation
- `executor.py` - Hook execution
- `api.py` - Hook API functions
- `handlers.py` - Pre/post tool handlers

### `/claude_parser/storage/`
Data persistence:
- `engine.py` - DuckDB engine (ONLY raw SQL execution)

## Data Flow

### 1. JSONL Loading
```
JSONL File → JSON.loads() → Pydantic Model → Dict
```

### 2. Query Execution
```
User Command → CLI Parser → Query Module → DuckDB → Results
```

### 3. Schema Normalization
```
Raw JSONL → NormalizedMessage → Consistent Interface
```

## Key Design Patterns

### Framework Delegation
```python
# GOOD - Framework handles everything
sessions = list(filter(None, (
    load_session(str(Path(path).expanduser()))
    for path in paths
)))

# BAD - Custom loop
sessions = []
for path in paths:
    session = load_session(path)
    if session:
        sessions.append(session)
```

### Pydantic Schema Normalization
```python
class NormalizedMessage(BaseModel):
    """Handles all JSONL schema variations"""
    uuid: Optional[str] = None
    type: Optional[str] = None
    timestamp: Optional[str] = None
    toolUseResult: Optional[Union[str, Dict[str, Any]]] = None

    @property
    def normalized_result(self) -> Dict[str, Any]:
        """Auto-normalize string or dict results"""
        if isinstance(self.toolUseResult, str):
            return json.loads(self.toolUseResult)
        return self.toolUseResult or {}
```

### Single Source of Truth
- One storage engine: `storage/engine.py`
- One session loader: `loaders/session.py`
- One discovery module: `loaders/discovery.py`
- Each query type in its own file

## Storage Architecture

### JSONL Structure
```json
{
  "uuid": "abc123def456",
  "type": "toolUseResult",
  "timestamp": "2024-01-15T10:30:00Z",
  "toolUseResult": {
    "type": "Write",
    "filePath": "/path/to/file.py",
    "content": "file content here"
  }
}
```

### DuckDB Integration
- Direct SQL queries on JSONL files
- No intermediate database
- Schema inference from JSON structure
- Efficient for large conversation files

## UUID System

Every Claude message gets a UUID, enabling:
- **Git-like commits**: Each UUID is like a commit SHA
- **Time travel**: Jump to any point in conversation
- **Partial matching**: Use first 6-8 chars like git
- **Cross-session search**: Find operations across all conversations

## Error Handling

All errors handled by frameworks:
- **Typer**: CLI validation and error messages
- **Pydantic**: Data validation and normalization
- **DuckDB**: SQL execution and file handling
- **Pathlib**: File system operations

## Performance Characteristics

- **Startup**: ~1-2 seconds (DuckDB initialization)
- **Query time**: <1 second for most operations
- **Memory**: Streaming processing, no full file loading
- **Scalability**: Handles GB-sized JSONL files efficiently

## Extension Points

### Adding New Commands
1. Create new file in `/cli/` (must be <80 LOC)
2. Import in `cg.py` orchestrator
3. Use existing query modules or create new ones

### Adding New Queries
1. Create file in `/queries/` for your feature
2. Use DuckDB SQL with JSONL
3. Return plain dicts/lists

### Adding New Operations
1. Create focused module in `/operations/`
2. Use framework delegation (no custom loops)
3. Re-export in `core.py` if needed

## Testing Approach

- **Real data**: Use actual JSONL files
- **No mocks**: Test with real Claude sessions
- **Framework validation**: Let Pydantic/Typer handle validation
- **Integration focus**: Test complete workflows

## Dependencies

Core dependencies (all framework delegation):
- **typer**: CLI framework
- **rich**: Terminal formatting
- **duckdb**: JSONL querying
- **pydantic**: Schema normalization
- **pathlib**: File operations

## Security Considerations

- **Read-only by default**: Most operations don't modify files
- **Explicit restore**: File restoration requires explicit commands
- **No credentials**: Works with local JSONL files only
- **Path validation**: Pathlib handles path security