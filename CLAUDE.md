# 🛡️ CLAUDE-PARSER WORKFLOW - ZERO TOLERANCE

## 🔴 MANDATORY FIRST STEPS (NO EXCEPTIONS)
```bash
pytest tests/ -x                    # MUST be 100% pass rate
python scripts/verify_spec.py       # MUST pass all quality gates  
python scripts/codebase_inventory.py --stats  # Explore before coding
```

## 🚨 QUALITY GATES (NON-NEGOTIABLE)
- **Tests**: 100% pass rate, 90%+ coverage
- **Architecture**: SOLID/DRY/DDD/TDD only
- **Files**: Max 150 LOC per file
- **Libraries**: 95% library, 5% glue code
- **Imports**: All dependencies validated
- **Research**: MANDATORY `research` tool before any implementation

## ⚡ WORKFLOW PRINCIPLES
1. **TDD**: Test → Code → Refactor (never Code → Test)
2. **DRY**: Find conceptual duplication, not just copy/paste
3. **Explore First**: Read existing code before writing new
4. **Library First**: Use `research` tool before any custom code
5. **Quality Gates**: Every commit must pass automated checks

## 🔍 RESEARCH FIRST - CRITICAL WORKFLOW
**⚠️  MANDATORY: Research before implementing anything!**

```bash
# Global research tool - use for ALL library decisions
research search "best Python library for parsing JSONL with TRUE 95/5"
research compare "JSON parsing libraries" 
research minimal "pydantic" "parse JSONL with validation"
```

**Why critical for claude-parser:**
- Finds parsing libraries that handle edge cases automatically
- Discovers validation frameworks (Pydantic) vs manual validation
- Prevents 200-line custom parsers when 5-line solutions exist
- Ensures SOLID/DDD compliance through library selection

**NEVER write parsers/validators without researching first!**

## 🔒 ENFORCEMENT (AUTOMATED)
```bash
# Pre-commit blocks bad commits
pre-commit install

# CI/CD blocks bad merges  
.github/workflows/quality-gates.yml

# One command validation
make quality-check
```

## 🏗️ CURRENT STATE REQUIREMENTS
- Fix 50 failing tests through architecture fixes
- Eliminate import dependency issues
- Complete DDD value objects (SessionId, MessageUuid, TokenCount)
- Establish proper dependency injection
- Implement missing integration tests

---
**VIOLATION = SESSION RESTART. NO EXCEPTIONS.**