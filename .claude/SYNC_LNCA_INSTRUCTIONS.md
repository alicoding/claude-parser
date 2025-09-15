# @SYNC_LNCA Migration Instructions
@NEURAL_TIMESTAMP: 2025-01-14T12:30:00Z

## For Other Claude Sessions - Run These Steps

### 1. Update Global CLAUDE.md
```bash
cp /Volumes/AliDev/ai-projects/claude-parser/.claude/GLOBAL_CLAUDE_NEW.md ~/.claude/CLAUDE.md
```

### 2. Create Local CLAUDE.md in Each Project
Each project needs its own `.claude/CLAUDE.md` with:
- Living document reference
- Codebase index
- Project-specific patterns

### 3. Remove LivingDocumentInjector Plugin
- Edit `pyproject.toml` (needs manual approval)
- Remove line: `living_document_injector = ...`
- Reinstall: `pip install -e .`

### 4. Key Changes to Understand
- **No more verbose hooks** - Use neural tags
- **No more plugins for docs** - Use native CLAUDE.md
- **@file references** - Load external files with @
- **Neural tags** - Define once, reference everywhere

### 5. Test @SYNC_LNCA
Say "@SYNC_LNCA" to:
- Load all patterns and workflows
- Update memory map
- Sync with other sessions

## Neural Tags Now Active
- `@MEMORY_MAP` - Pathways not content
- `@CONTEXT_DEDUP` - No duplicate injection
- `@INTENT_PARSING_REQUIRED` - Parse intent first
- `@LNCA_ENFORCEMENT` - Zero tolerance

## Migration Complete When
1. Global CLAUDE.md uses neural tags
2. Local CLAUDE.md has @file references
3. Hooks output neural tags not verbose text
4. Living doc plugin removed
5. @SYNC_LNCA command works