# 🧠 claude-parser Memory Map
@NEURAL_TIMESTAMP: 2025-01-14T15:00:00Z
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

## Recent Discoveries
- `@CH_HOOK_ISSUE_FIXED` → 2025-01-14: Fixed logger output to comply with Anthropic JSON spec
- `@STEVEDORE_FIXED` → Installed stevedore dependency (2025-01-14)
- `@DISCORD_FILES_MISSING` → discord_conversation.py imports discord_notifier/blocker but files don't exist
- `@CG_ADVANCED_COMMANDS` → 2025-01-14: find ✓, blame ✓, reflog ✓, show ✓
- `@QUERY_UTILS_CREATED` → queries/query_utils.py - Solves schema mismatch DRY violation
- `@CG_REFACTORED` → Split into cg.py, cg_advanced.py, cg_reflog.py for LOC compliance
- `@AUDIT_ON_READ_ADDED` → patterns.md:75 - Enforces violation detection on every Read
- `@MY_MISTAKE` → I created then deleted discord files - they need to be restored from Claude history
- `@DISCOVERY_DRY_VIOLATION` → 2025-01-14: discovery/core.py reimplements loaders/discovery.py
- `@MEMORY_MAP_LOC_VIOLATION` → memory_map.md itself is 110 lines - needs splitting

## Update Triggers
- On file creation/deletion
- On function rename
- On module restructure
- Every @SYNC_LNCA execution

## JSONL Schema Fields
- `uuid` → Unique message identifier
- `parentUuid` → Message chain navigation
- `timestamp` → ISO timestamp ordering
- `message.content[].name` → Tool name (Write/Edit/MultiEdit)
- `message.content[].input.file_path` → Target file
- `toolUseResult.content` → Full file content for restoration
- `toolUseResult.oldString/newString` → Track changes
- `message.usage.input_tokens/output_tokens` → Token tracking
- **Power**: Every tool operation is reversible via JSONL!