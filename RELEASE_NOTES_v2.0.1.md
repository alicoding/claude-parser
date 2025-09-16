# Release Notes - v2.0.1

## Security & Bug Fix Release
**Date**: 2025-09-15

## 🔒 Security Fixes
- **CRITICAL**: Removed test credentials and sensitive data from production package
- Deleted test_folder/, test-archive/, and other test files from distribution
- Cleaned up empty domain folders that were unnecessarily inflating package size

## 🐛 Bug Fixes

### Discord Stop Hook Fix
- **Issue**: get_latest_claude_message() was returning None for messages with tool_use content
- **Cause**: Filter was incorrectly excluding assistant messages containing tool operations
- **Fix**: Updated exclude_tool_operations() to properly handle assistant messages with tools

### API UX Improvement
- **Issue**: get_latest_claude_message() returned complex nested object structure
- **Before**: Returned entire message object with content buried in nested fields
- **After**: Returns simple string with just the message text
- **Impact**: Much cleaner API for plugin developers

### Filters.py LOC Compliance
- **Issue**: File was 82 lines, violating LNCA's 80 line limit
- **Fix**: Refactored to comply with LOC enforcement

## 📁 Cleanup
- Removed empty directories: domain/, application/, infrastructure/, utils/
- Removed test files: test_single.py, verify_spec.py
- Total cleanup: ~10 empty directories and test files removed

## 🧪 Testing
- Added black box tests for Stop hook functionality
- Tests now use real JSONL data instead of mocks
- Improved test coverage for hook request handling

## 📚 Documentation
- Created comprehensive bug reports for semantic-search service
- Updated memory map with Discord Stop hook flow
- Documented dogfooding cycle between claude-parser and semantic-search

## 🔄 Dogfooding Discoveries
- First production use of semantic-search MCP service
- Found and reported keyword matching bug in semantic search
- Established mutual improvement cycle with semantic-search project

## 💡 Lessons Learned
- Semantic search needs code-aware embeddings, not just keyword matching
- API design should hide complexity, expose simplicity
- Dogfooding with real projects finds real bugs

## 🚀 Upgrade Instructions
```bash
pip install --upgrade claude-parser==2.0.1
```

## ⚠️ Breaking Changes
None - This is a backward compatible bug fix release

## 🙏 Acknowledgments
Thanks to the lnca-plugins Discord integration for helping us discover these bugs!

---
*This is a security and bug fix release. All users should upgrade immediately.*