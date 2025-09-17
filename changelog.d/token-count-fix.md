### Fixed

- **Token Counting**: Fixed token counting to match Claude Code UI's `/context` command
  - Now correctly counts compact summary content + user message content + assistant usage tokens
  - Added `count_session_tokens()` function for consistent API interface
  - Fixed `isCompactSummary` field name mismatch (was `is_compact_summary`)
  - Improved SQL queries to include cache_read_input_tokens for accurate counts
  - Token counts now match UI within 96% accuracy (6,341 vs 6,600 target)