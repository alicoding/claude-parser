# claude-parser - Living Document (CONDENSED)
Generated: 2025-09-10T18:03:15
Updated: 2025-09-15T01:55:00
@NEURAL_TIMESTAMP: 2025-09-15T01:55:00Z

## 📚 Documentation Index
- **Architecture**: `.claude/docs/architecture_map.md`
- **DuckDB Migration**: `.claude/docs/duckdb_migration.md`
- **Hooks**: `claude_parser/hooks/README.md`
- **LNCA Patterns**: `lnca-plugins/config/patterns.yml` and `workflows.yml`

## 🎯 LIVING DOC RULES
- **Max Size**: 7000 words (~10K tokens)
- **Growth Rate**: ~1700 words/day = prune aggressively
- **Keep**: Patterns, architectures, decisions
- **Remove**: Diary logs, verbose details, duplicates
- **Neural Tags**: @CONTEXT_DEDUP - Define once, reference everywhere

## 🔑 Pattern Index (Neural Tags Only)

### Architecture
- **LNCA**: @COMPOSABLE_ARCHITECTURE → `patterns.yml:103`
- **DuckDB**: @SINGLE_SOURCE_TRUTH → `archive/2025-01-12_duckdb.md`
- **Hooks**: @FRAMEWORK_FIRST → `hooks/README.md`
- **Plugin Loading**: Entry point name must match → `plugin_manager.py:28`

### Critical Patterns
- @LOC_ENFORCEMENT → `patterns.yml:13`
- @LIVING_DOC_PRUNING → `patterns.yml:43`
- @DRY_FIRST → `patterns.yml:41`
- @CONTEXT_DEDUP → `patterns.yml:48`
- @INTENT_PARSING_REQUIRED → `patterns.yml:45`

### Anti-Patterns
- @GOD_OBJECT → Fixed 2025-01-13
- @MANUAL_LOOPS → Fixed 2025-01-12
- @FRAMEWORK_BYPASS → `patterns.yml:47`

## 📝 Decision Memory (Key Points Only)
- **2025-09-15**: @SECURITY_CLEANUP → Removed secrets-to-remove.txt with API keys from repo, archived old docs
- **2025-09-15**: @V2_RELEASE_READY → Prepared complete v2.0.0 release with docs, GitHub Actions, comprehensive README
- **2025-09-15**: @CORRECT_CLAUDE_PATH → Fixed documentation - actual path is ~/.claude/projects/ NOT ~/.claude/code/conversations/
- **2025-09-15**: @COMPLETE_DOMAIN_MAPPING → Discovered 15 total domains (was missing 4: filtering, watch, messages, models)
- **2025-09-15**: @CH_COMMAND_DISCOVERED → Composable hook runner CLI for pluggable executors
- **2025-09-15**: @DOCUMENTATION_COMPLETE → Full MkDocs + LlamaIndex auto-generation system operational!
- **2025-09-15**: @CG_DISASTER_TESTING → Completed CG refactoring with Pydantic schema normalization
- **2025-09-15**: @LOC_ENFORCEMENT_COMPLIANCE → Split 347-line cg.py into <80 LOC modular files
- **2025-09-15**: @ZERO_CUSTOM_CODE_COMPLIANCE → All CG commands use framework delegation only
- **2025-09-15**: @PYDANTIC_SCHEMA_MODELS → schema_models.py for JSONL normalization instead of custom parsing
- **2025-01-14**: Neural tags in hooks - no verbose messages → `patterns.yml:45-51`
- **2025-01-14**: @MEMORY_MAP pattern - pathways not content
- **2025-01-14**: Living doc pruning - 5292→341 words (94% reduction)
- **2025-01-13**: HookRequest API - clean separation of concerns
- **2025-01-12**: DuckDB migration - @SINGLE_SOURCE_TRUTH
- **2025-09-11**: Checkpoint detection - 28 LOC using existing SDK

## 🏗️ Current Architecture
- **Hooks v3**: HookRequest API with dynamic import_module (NOT pluggy)
- **Core Modules**: 85% LNCA compliant
- **Performance**: 2-3 second response (was >2min)
- **Token Counting**: Fixed user vs assistant separation

## 🧠 Codebase Index (@MEMORY_MAP)
**Hooks**: `hooks/` → request.py (data), aggregator.py (JSON), executor.py (runner)
**Storage**: `storage/engine.py` → DuckDB queries only here
**Tokens**: `tokens/` → context.py (window calc), billing.py (costs)
**Plugins**: `lnca-plugins/` → 7 plugins via pluggy
**Navigation**: `navigation/core.py` → message filtering

## ⚠️ Critical Learnings
1. **Memory Map**: Know WHERE not WHAT - pathways not content
2. **Neural Navigation**: feature→file→line not implementation
3. **Context Dedup**: Define once, reference everywhere
4. **LOC Violations**: Analyze WHY before splitting
5. **Pattern Enforcement**: Workflows enforce, patterns suggest
6. **PATHWAY RULE**: Files without @reference in CLAUDE.md = invisible to next session
7. **@LNCA_ENFORCEMENT**: Must appear in EVERY message - zero tolerance

---
*Archived entries moved to `.claude/archive/` - See full history there*