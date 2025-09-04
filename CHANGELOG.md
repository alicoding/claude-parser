# Changelog

All notable changes to Claude Parser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - Git-Like CLI & Multi-Session Support

### Added - Git-Style Interface & Multi-Session Intelligence

#### New `cg` Command Interface
- **Git-like CLI**: Short `cg` (claude-git) command for intuitive navigation
- **Auto-detection**: Finds Claude Code projects from current working directory
- **Multi-session support**: Aggregates operations across all Claude Code sessions
- **Cross-platform**: Support for `~/.claude/projects` on macOS/Linux

#### Core Navigation Commands
- `cg status` - Project state and multi-session information
- `cg log` - Operation history across all sessions with session context
- `cg checkout <uuid>` - Restore files to exact state at any operation
- `cg undo <n>` - Go back N operations across all files and sessions
- `cg show <uuid>` - Detailed view of specific operations with session metadata
- `cg diff` - Compare states between operations or current vs previous
- `cg reset <uuid>` - Reset to specific operation state (git-style)

#### Multi-Session Intelligence
- **Session detection**: Automatically discovers concurrent Claude Code sessions
- **Chronological ordering**: Operations ordered by timestamp across sessions
- **Session context**: Shows which session created each operation `[abc12345]`
- **Cross-session navigation**: Undo/redo works seamlessly across session boundaries
- **Conflict resolution**: Tools for understanding overlapping file modifications

#### Enhanced Backend Services
- **RealClaudeTimeline**: Processes authentic Claude Code JSONL structure
- **Multi-session discovery**: `find_all_transcripts_for_cwd()` aggregates all project sessions
- **UUID-based navigation**: Native support for Anthropic's conversation UUID system
- **Git integration**: Each Claude operation creates git commit for precise state tracking
- **Real tool operation support**: Handles Read, Edit, MultiEdit, Write operations

### Added - Previous Features
- Full Domain-Driven Design (DDD) architecture implementation
- Enterprise-grade repository structure with clean separation of concerns
- 95/5 research workflow integration with mandatory library research
- Publishing pipeline to PyPI with GitHub Actions
- Comprehensive test coverage (86%+)
- Hook system for input/output processing
- Watch API for real-time file monitoring
- Discovery tools for finding Claude transcripts
- NetworkX integration for thread navigation and graph analysis

### Changed
- **Enhanced CLI**: Extended existing CLI with git-like `cg` commands
- **Discovery service**: Added multi-session transcript discovery
- **Timeline processing**: Upgraded to handle real Claude Code JSONL format
- **Documentation**: Added comprehensive multi-session workflow guides
- Migrated from simple module structure to full DDD layers
- Improved JSON parsing performance with orjson (10x faster)
- Enhanced type safety with Pydantic v2
- Refactored message parsing to extract embedded tool uses
- Updated Python requirement to 3.11+ for modern features

### Fixed
- **Multi-session concurrency**: Resolved data loss when multiple Claude sessions modify same files
- **UUID navigation**: Fixed checkout failures with partial UUIDs
- **Cross-platform paths**: Standardized `~/.claude/projects` path handling
- **Session isolation**: Proper aggregation without operation conflicts
- Tool extraction from assistant messages with embedded content
- Message parsing for complex content arrays
- Thread navigation with proper graph traversal
- Edge case handling in JSONL parsing

## [0.1.0] - 2025-08-21

### Added
- Initial release with basic JSONL parsing
- Support for Claude Code conversation format
- Message type hierarchy (User, Assistant, Tool, Summary)
- Basic conversation analysis features
