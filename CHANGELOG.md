## [2.0.1] - 2025-09-15

# Changelog

All notable changes to claude-parser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- towncrier release notes start -->



### Security Fixes

- Removed test credentials and sensitive data from production package (test_folder/, test-archive/) (#1)

### Removed

- Cleaned up empty directories (domain/, application/, infrastructure/, utils/) reducing package size (#4)

### Changed

- get_latest_claude_message() now returns simple string instead of complex nested object for better API UX (#3)

### Fixed

- Fixed Discord stop hook bug where get_latest_claude_message() returned None for messages with tool_use content (#2)
# Changelog

All notable changes to claude-parser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Git-Like CLI Interface & Multi-Session Support

#### New `cg` Command
- **Git-style CLI**: Short `cg` (claude-git) command for intuitive operation navigation
- **Auto-detection**: Automatically finds Claude Code projects from current working directory
- **Cross-platform paths**: Support for `~/.claude/projects` directory structure (macOS/Linux)

#### Core Commands
- `cg status` - Show project state and multi-session information
- `cg log` - View operation history across all Claude Code sessions
- `cg checkout <uuid>` - Restore files to exact state at any operation
- `cg undo <n>` - Go back N operations across all files and sessions
- `cg show <uuid>` - Detailed view of specific operations
- `cg diff` - Compare states between operations
- `cg reset <uuid>` - Reset to specific operation state

#### Multi-Session Intelligence
- **Session Detection**: Automatically discovers all Claude Code sessions per project
- **Chronological Aggregation**: Orders operations across sessions by timestamp
- **Session Context**: Shows which session created each operation
- **Cross-Session Navigation**: Undo/redo works seamlessly across session boundaries
- **Conflict Resolution**: Tools for understanding overlapping file changes

#### Enhanced Services
- **RealClaudeTimeline**: Processes authentic Claude Code JSONL format
- **Multi-Session Discovery**: `find_all_transcripts_for_cwd()` finds all project sessions
- **UUID-based Navigation**: Native support for Anthropic's UUID system
- **Git Integration**: Each Claude operation creates a git commit for precise tracking

#### Documentation
- **Command Reference**: Complete `cg` command documentation with examples
- **Multi-Session Guide**: Comprehensive guide for concurrent session workflows
- **Real-world Scenarios**: Practical examples for common multi-session situations
- **Troubleshooting**: Setup verification and common issue resolution

### Technical Enhancements

#### Authentication Claude Code Integration
- **Real JSONL Processing**: Handles authentic Claude Code conversation exports
- **Tool Operation Support**: Read, Edit, MultiEdit, Write operations
- **Session Metadata**: Complete session ID, timestamp, and context tracking
- **Parent UUID Chains**: Maintains conversation flow relationships

#### Architecture Improvements
- **SOLID Design**: Clean separation between discovery, timeline, and navigation services
- **DRY Principle**: Reuses existing git, typer, and rich library functionality
- **95/5 Implementation**: Maximum library leverage, minimal custom code
- **Platform Support**: Unix-like systems with standard `~/.claude/projects` structure

#### Performance & Reliability
- **Efficient Processing**: Chronological operation sorting with O(n log n) complexity
- **Git-based Storage**: Leverages GitPython for reliable state management
- **Cache Management**: Automatic cleanup of temporary git repositories
- **Error Handling**: Graceful handling of malformed JSONL and missing operations

### Testing
- **Real Data Tests**: Test suite using authentic Claude Code JSONL files
- **Multi-Session Coverage**: Validates concurrent session handling
- **Integration Tests**: End-to-end workflow testing from discovery to restoration
- **Cross-Platform Verification**: Ensures consistent behavior on macOS/Linux

### Documentation Updates
- **README Enhancement**: Added `cg` command examples and multi-session workflows
- **API Documentation**: Updated with new services and capabilities
- **Usage Examples**: Real-world scenarios and troubleshooting guides
- **Architecture Documentation**: Technical implementation details

## [Previous Versions]

### [0.x.x] - 2024-xx-xx
- Initial SDK implementation with parsing capabilities
- CLI tools for basic JSONL processing
- Domain-driven design architecture
- Memory export functionality
- Real-time file watching with UUID checkpoints

---

## Platform Support

### Currently Supported
- ✅ **macOS**: Full support with `~/.claude/projects` auto-detection
- ✅ **Linux**: Full support with `~/.claude/projects` auto-detection
- ✅ **Claude Code**: Processes authentic conversation exports

### Planned Support
- ⏳ **Windows**: Cross-platform path detection for Windows Claude Code installations
- ⏳ **Custom Paths**: Configurable Claude Code directory locations

## Migration Guide

### For Existing Users
- **CLI Compatibility**: All existing `claude-parser` commands remain unchanged
- **New Features**: `cg` commands provide additional functionality alongside existing tools
- **Auto-Discovery**: No configuration needed - works with existing `~/.claude/projects` setup

### New Features Usage
```bash
# New git-like interface
cg status                    # Project overview
cg log --file app.py         # File history
cg undo 3                    # Time travel

# Existing functionality (unchanged)
claude-parser parse file.jsonl
claude-parser find
claude-parser projects
```

## Breaking Changes
None. All existing functionality is preserved.

## Contributors
- Enhanced multi-session support and git-like CLI interface
- Real Claude Code JSONL processing implementation
- Cross-platform path handling for macOS/Linux
- Comprehensive documentation and testing

---

**Note**: This release focuses on authentic Claude Code integration and multi-session workflows. The `cg` command provides a git-like interface while preserving all existing SDK functionality.
