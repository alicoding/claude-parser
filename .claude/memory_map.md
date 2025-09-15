# 🧠 claude-parser Memory Map
@NEURAL_TIMESTAMP: 2025-09-15T01:56:00Z
@MEMORY_MAP @NEURAL_MIND_MAP @PATHWAY_NAVIGATION

## Core Navigation Pathways

### Hooks System
- `@HOOK_REQUEST` → hooks/request.py:HookRequest
- `@HOOK_AGGREGATOR` → hooks/aggregator.py:aggregate_responses()
- `@HOOK_EXECUTOR` → hooks/executor.py:execute_hook()
- `@HOOK_API` → hooks/api.py:process_request()

### Storage Layer (REFACTORED 2025-01-14)
- `@DUCKDB_ENGINE` → storage/engine.py:execute() **ONLY raw SQL**
- `@ANTI_PATTERN_FIXED` → Removed god object from engine.py
- `@QUERY_MODULES` → queries/*.py - One file per feature:
  - session_queries.py → load_jsonl()
  - token_queries.py → count_tokens()
  - find_queries.py → find_files()
  - blame_queries.py → blame_file()
  - reflog_queries.py → get_reflog()

### Token Management
- `@TOKEN_CONTEXT` → tokens/context.py:calculate_window()
- `@TOKEN_BILLING` → tokens/billing.py:calculate_cost()
- `@TOKEN_STATUS` → tokens/status.py:get_usage()

### Navigation (POWER TOOLS)
- `@NAV_CORE` → navigation/core.py:filter_messages()
- `@NAV_TIMELINE` → navigation/timeline.py:**UUID time travel - find/extract any state**
  - find_message_by_uuid() → Jump to any operation
  - get_message_sequence() → Extract range of operations
  - get_timeline_summary() → Overview of all checkpoints
- `@NAV_CHECKPOINT` → navigation/checkpoint.py:**Recovery points - detect safe states**
  - find_current_checkpoint() → Last file operation
  - _find_triggering_user_message() → What caused the change
- `@NAV_SESSION` → navigation/session_boundaries.py:find_boundaries()

### CLI Commands
- `@CLI_CG` → cli/cg.py:**Every API call = automatic git commit**
  - `cg status` → IMPLEMENTED: Like git status
  - `cg log` → IMPLEMENTED: Like git log
  - `cg diff` → @CG_PHASE_4: Like git diff
  - `cg checkout <file|uuid>` → @CG_PHASE_4: Like git checkout
  - `cg reset [--hard] <uuid>` → @CG_PHASE_4: Like git reset
  - `cg revert <uuid>` → @CG_PHASE_4: Like git revert
  - `cg blame <file>` → @CG_PHASE_4: Like git blame
  - `cg stash/pop` → @CG_PHASE_4: Like git stash
  - **INSIGHT**: Each Claude message has UUID = commit SHA!
- `@CLI_CH` → cli/ch.py:main_handler()

### Analytics
- `@ANALYTICS_CORE` → analytics/core.py:analyze_session()
- `@ANALYTICS_BILLING` → analytics/billing.py:calculate_usage()
- `@ANALYTICS_TOOLS` → analytics/tools.py:analyze_tool_usage()
- `@ANALYTICS_PROJECTS` → analytics/projects.py:get_project_stats()

### Session Management
- `@SESSION_CORE` → session/core.py:load_session()
- `@SESSION_LOADER` → loaders/session.py:SessionLoader

### Discovery
- `@DISCOVERY_CORE` → discovery/core.py:**99 LOC VIOLATION + DRY VIOLATION**
- `@DISCOVERY_LOADER` → loaders/discovery.py:discover_all_sessions() **CORRECT implementation**

### Filtering
- `@FILTER_CORE` → filtering/filters.py:apply_filters()

### Watch System
- `@WATCH_CORE` → watch/core.py:watch_files()

### Main Entry
- `@MAIN_APP` → main.py:app()

## Pattern References
- `@SINGLE_SOURCE_TRUTH` → patterns.yml:11
- `@LOC_ENFORCEMENT` → patterns.yml:13
- `@MEMORY_MAP` → patterns.yml:55
- `@NEURAL_MIND_MAP` → patterns.yml:58

## Anti-Pattern Locations
- `@MISSING_MIND_MAP` → patterns.yml:100
- `@CONTENT_STORAGE` → patterns.yml:101

## Documentation System (COMPLETE 2025-09-15)
- `@DOCS_API` → docs/api/generated.md:**LlamaIndex-generated API reference**
- `@DOCS_ARCHITECTURE` → docs/architecture/overview.md:**System design documentation**
- `@DOCS_USER_GUIDE` → docs/user-guide/usage.md:**Getting started guide**
- `@DOCS_INSTALLATION` → docs/installation.md:**Setup instructions**
- `@DOCS_GENERATOR` → **100% framework delegation via LlamaIndex QueryEngine**
- `@DOCS_AUTOMATION` → **Post-commit hooks for incremental updates**

## Filtering Domain (DISCOVERED 2025-09-15)
- `@FILTER_MESSAGES` → filtering/filters.py:**Message filtering functions**
  - filter_messages_by_type() → Filter by user/assistant/system
  - filter_messages_by_tool() → Filter by tool usage
  - search_messages_by_content() → Content search
  - filter_hook_events_by_type() → Hook event filtering
  - filter_pure_conversation() → Get conversation without tools
  - exclude_tool_operations() → Remove tool messages

## Watch Domain (DISCOVERED 2025-09-15)
- `@WATCH_CORE` → watch/core.py:**Real-time file monitoring**
  - watch() → Watch JSONL files for changes with callbacks

## Messages Domain
- `@MESSAGES` → messages/:**Message processing utilities**

## Models Domain
- `@MODELS` → models/:**Data models and utilities**

## CH Command (DISCOVERED 2025-09-15)
- `@CLI_CH` → cli/ch.py:**Composable hook runner**
  - `ch run --executor <module>` → Execute hooks with pluggable executors
  - Reads from stdin, outputs per Anthropic spec
  - Environment var: CLAUDE_HOOK_EXECUTOR

## Complete Domain List (15 total)
1. analytics/ - Session and tool analysis
2. cli/ - CG and CH commands
3. discovery/ - File and project discovery
4. filtering/ - Message filtering (**NEW**)
5. hooks/ - Hook system and API
6. loaders/ - Session and file loading
7. messages/ - Message utilities (**NEW**)
8. models/ - Data models (**NEW**)
9. navigation/ - Timeline and UUID navigation
10. operations/ - File operations and restoration
11. queries/ - DuckDB SQL queries
12. session/ - Session management
13. storage/ - DuckDB engine
14. tokens/ - Token counting and billing
15. watch/ - Real-time monitoring (**NEW**)

## Recent Discoveries
- `@V2_RELEASE_READY` → 2025-09-15: Complete v2.0.0 release package with docs, GitHub Actions, README
- `@CORRECT_CLAUDE_PATH` → 2025-09-15: Actual Claude path is ~/.claude/projects/ NOT ~/.claude/code/conversations/
- `@CG_DISASTER_TESTING` → 2025-09-15: Testing "oh shit" recovery scenarios
- `@PYDANTIC_SCHEMA_NORMALIZATION` → 2025-09-15: Framework delegation for JSONL parsing
- `@DOCUMENTATION_COMPLETE` → 2025-09-15: Full MkDocs + LlamaIndex auto-generation working!
- `@COMPLETE_DOMAIN_MAPPING` → 2025-09-15: Discovered 4 unmapped domains (filtering, watch, messages, models)

See: `.claude/docs/memory_map_extended.md` for full details