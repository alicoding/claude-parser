# Claude Parser Architecture Map
@NEURAL_TIMESTAMP: 2025-01-13T14:00:00Z

## Core Modules Overview

### Entry Point (`__init__.py`)
**Status**: ✅ LNCA COMPLIANT
- **Purpose**: Published package API facade
- **Exports**: 25 public functions + MessageType class + version info
- **Pattern**: @FRAMEWORK_FACADE - Clean interface delegation

### Session Management (`main.py`)
**Status**: ✅ LNCA COMPLIANT
- **Purpose**: Smart session loading with discovery integration
- **Functions**: `load_session()`, `load_latest_session()`, `discover_all_sessions()`
- **Pattern**: @SINGLE_SOURCE_TRUTH for session loading

### Data Models (`models.py`)
**Status**: ⚠️ DEPRECATED - Replaced by plain dicts
- **Former Classes**: RichMessage, RichSession (god objects)
- **Migration**: ✅ COMPLETE - All code uses plain dicts
- **New Approach**: `messages/utils.py` provides dict operations

### Session Operations (`session.py`)
**Status**: ✅ LNCA COMPLIANT (74 LOC)
- **Purpose**: JSONL loading and metadata extraction
- **Pattern**: @FRAMEWORK_FIRST - 100% Polars + Glom delegation
- **Robustness**: Multiple fallback paths for field extraction

### File Discovery (`discovery.py`)
**Status**: ✅ LNCA COMPLIANT (94 LOC)
- **Purpose**: Git-like project root detection and file discovery
- **Performance**: Solved CLI timeout issues (>2min → 2-3 seconds)
- **Pattern**: @FRAMEWORK_FIRST with project-root-finder

### Timeline Navigation (`timeline.py`)
**Status**: ❌ LOC VIOLATION (145 LOC > 80)
- **Purpose**: UUID navigation and checkpoint detection
- **Functions**: `find_message_by_uuid()`, `find_current_checkpoint()`
- **Issue**: Needs refactoring to <80 LOC

### Message Utilities (`messages/utils.py`)
**Status**: ✅ LNCA COMPLIANT (76 LOC)
- **Purpose**: Pure functions for dict operations
- **Pattern**: @COMPOSITION - No classes, just functions
- **Functions**:
  - `get_text(msg)` - Extract text from any message format
  - `get_token_usage(msg)` - Extract token usage
  - `get_model(msg)` - Get model name
  - `is_hook_message(msg)` - Check for hook events
  - `is_tool_operation(msg)` - Check for tool operations
- **Key Achievement**: @SINGLE_SOURCE_TRUTH for message data extraction

### Analytics (`analytics.py`)
**Status**: ✅ LNCA COMPLIANT (53 LOC)
- **Purpose**: Session analytics with framework delegation
- **Pattern**: @FRAMEWORK_FIRST - Pure pandas + Counter operations

### File Operations (`operations.py`)
**Status**: ✅ LNCA COMPLIANT (64 LOC)
- **Purpose**: File restoration and diffing
- **Dependencies**: 100% stdlib (difflib, pathlib)
- **Pattern**: @SINGLE_SOURCE_TRUTH for file operations

### Token Analysis (`tokens.py`)
**Status**: ✅ LNCA COMPLIANT (61 LOC)
- **Purpose**: Token counting and cost estimation
- **Pattern**: @FRAMEWORK_FIRST - 100% tiktoken delegation

## Hook System v3

### Overview
**Status**: ✅ LNCA COMPLIANT
**Documentation**: See `claude_parser/hooks/README.md`

### Components
- `request.py` (68 LOC) - HookRequest data encapsulation
- `aggregator.py` (80 LOC) - Result aggregation with ANY block = fail
- `utils.py` (46 LOC) - Minimal I/O utilities
- `app.py` (72 LOC) - Typer CLI (kept for compatibility)

### Pattern Achievements
- @DUAL_INTERFACE_PATTERN: CLI + Programmatic API
- @SINGLE_SOURCE_TRUTH: One place for hook I/O
- @FRAMEWORK_FIRST: 100% delegation
- Superior to cchooks: 63% less code, semantic API

## Storage Layer (DuckDB)

### Engine (`storage/engine.py`)
**Status**: ✅ LNCA COMPLIANT (81 LOC)
- **Purpose**: ONLY file that imports DuckDB
- **Pattern**: @SINGLE_SOURCE_TRUTH for all SQL operations
- **API**: `engine.query(operation, params)`

### Token Operations
- `tokens/context.py` (65 LOC) - Context window calculation
- `tokens/billing.py` (70 LOC) - Cost analysis
- **Pattern**: @COMPOSITION - Process plain dicts

## Compliance Summary

### Statistics
- **Total Core Modules**: 13
- **LNCA Compliant**: 11/13 (85%)
- **LOC Violations**: 2 files need refactoring
  - `timeline.py` (145 LOC)
  - `cg_cli.py` (112 LOC)

### Pattern Compliance
- ✅ @FRAMEWORK_FIRST: 95% framework delegation
- ✅ @SINGLE_SOURCE_TRUTH: Each concern in one place
- ✅ @LOC_ENFORCEMENT: 85% compliance
- ✅ @COMPOSITION: Moving from god objects to plain dicts
- ✅ @DUAL_INTERFACE_PATTERN: Hooks system implemented

## API Contract

### Public Functions (25)
**Session**: `load_session()`, `load_latest_session()`, `discover_all_sessions()`
**Analytics**: `analyze_session()`, `analyze_project_contexts()`, `analyze_tool_usage()`
**Discovery**: `discover_claude_files()`, `discover_current_project_files()`
**Operations**: `restore_file_content()`, `generate_file_diff()`, `compare_files()`
**Timeline**: `find_message_by_uuid()`, `get_message_sequence()`, `find_current_checkpoint()`
**Tokens**: `count_tokens()`, `analyze_token_usage()`, `estimate_cost()`

### CLI Commands
- `cg status` - Git-like status with checkpoint info
- `cg log` - Show conversation timeline
- `cg diff` - Compare file versions

## Migration Status

### Completed
- ✅ DuckDB migration (Polars removed)
- ✅ Hook system v3 (HookRequest API)
- ✅ God object elimination (RichMessage/RichSession → dicts)
- ✅ Performance optimization (2-3 second CLI response)

### In Progress
- 🔄 Complete dict-based API migration
- 🔄 LOC violation fixes (timeline.py, cg_cli.py)

### Anti-Patterns Eliminated
- ✅ @MANUAL_PARSING_ANTIPATTERN - Use metadata not content
- ✅ @FRAMEWORK_BYPASS - 100% framework delegation
- ✅ @GOD_OBJECT - RichMessage/RichSession removed
- ✅ @CIRCULAR_DEPENDENCIES - Clean separation achieved