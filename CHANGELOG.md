# Changelog

All notable changes to Claude Parser will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Migrated from simple module structure to full DDD layers
- Improved JSON parsing performance with orjson (10x faster)
- Enhanced type safety with Pydantic v2
- Refactored message parsing to extract embedded tool uses
- Updated Python requirement to 3.11+ for modern features

### Fixed
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