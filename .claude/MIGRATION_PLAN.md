# CLAUDE.md Architecture Migration Plan
@NEURAL_TIMESTAMP: 2025-01-14T12:00:00Z

## Current State (INEFFICIENT)
- Plugin manually injects living document
- Global CLAUDE.md has verbose instructions
- Manual file reading at session start
- Duplicate content in context

## Target State (EFFICIENT)
### Global CLAUDE.md (`~/.claude/CLAUDE.md`)
```markdown
# 🎯 LNCA Framework
@SYNC_LNCA @MEMORY_MAP @CONTEXT_DEDUP @LNCA_ENFORCEMENT

## Core Patterns
@/Volumes/AliDev/ai-projects/lnca-plugins/.claude/docs/patterns.md
@/Volumes/AliDev/ai-projects/lnca-plugins/.claude/docs/workflows.md

## Project Paths
- **claude-parser**: `/Volumes/AliDev/ai-projects/claude-parser/`
- **lnca-plugins**: `/Volumes/AliDev/ai-projects/lnca-plugins/`
```

### Local CLAUDE.md (`project/.claude/CLAUDE.md`)
```markdown
# Project Living Document
@MEMORY_MAP @NEURAL_NAVIGATION

## Memory Map
@./.claude/docs/memory_map.md
@./.claude/docs/codebase_index.md
@./.claude/living_document.md
```

## Migration Steps
1. **Extract patterns.yml → patterns.md** (markdown format)
2. **Extract workflows.yml → workflows.md** (markdown format)
3. **Update global CLAUDE.md** with neural tags only
4. **Setup local CLAUDE.md** with @file references
5. **Remove LivingDocumentInjector plugin**
6. **Test @SYNC_LNCA command**

## Benefits
- Native Claude Code feature (no plugins)
- Composable documentation
- Efficient updates (only deltas)
- Clear global/local separation
- Neural tags instead of verbose text