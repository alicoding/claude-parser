# claude-parser Project
@MEMORY_MAP @NEURAL_NAVIGATION @CODEBASE_INDEX @LNCA_ENFORCEMENT

## Living Document
@./.claude/living_document.md

## Neural Architecture
@./.claude/NEURAL_TAG_ARCHITECTURE.md

## Memory Map
@./.claude/memory_map.md

## CG Implementation Roadmap
@./.claude/CG_IMPLEMENTATION_ROADMAP.md

## CG LNCA Compliant Plan
@./.claude/CG_LNCA_COMPLIANT_PLAN.md

## Codebase Index
- **Hooks**: `hooks/` → request.py, aggregator.py, executor.py
- **Storage**: `storage/engine.py` → DuckDB (ONLY file)
- **Tokens**: `tokens/` → context.py, billing.py
- **Navigation**: `navigation/core.py` → filtering

## Recent Decisions
- Neural tags replace verbose hooks
- Entry points must match in plugin manager
- Living doc max 7000 words → prune to tags
- @MEMORY_MAP for pathways not content

## Architecture Patterns
- @SINGLE_SOURCE_TRUTH → One file per feature
- @FRAMEWORK_FIRST → 80% framework usage
- @LOC_ENFORCEMENT → <80 lines per file
- @CONTEXT_DEDUP → Define once reference many