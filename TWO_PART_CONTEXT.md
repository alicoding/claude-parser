# CRITICAL: Two-Part Task Context System

## WHY THIS EXISTS
Without this, Claudes hallucinate and create 2,553 lines instead of 200.

## THE TWO PARTS - BOTH REQUIRED

### PART 1: CLAUDE FILLS (Your Decisions)
These are DESIGN DECISIONS that YOU (Claude) must make:

```yaml
95/5 Rule:
  Library to use: [YOU DECIDE: e.g., "toolz for functional"]
  Don't build: [YOU DECIDE: e.g., "custom loops"]

DRY:
  Existing code to reuse: [YOU SEARCH & DECIDE]
  Don't duplicate: [YOU IDENTIFY]

SOLID:
  Single Responsibility: [YOU DEFINE]
  Dependencies: [YOU SPECIFY]

DDD:
  Layer: [YOU CHOOSE: domain|infrastructure|application]
  Boundaries: [YOU DEFINE]

TDD:
  Test file: [YOU NAME IT]
  Coverage: [YOU SET TARGET]
```

### PART 2: AUTO-GENERATED (Facts)
These are FACTS from actual commands:

```yaml
Research: [OUTPUT from research.py]
Duplicates: [OUTPUT from grep -r]
Complexity: [OUTPUT from radon cc]
File Sizes: [OUTPUT from wc -l]
Coverage: [OUTPUT from pytest --cov]
```

## WORKFLOW FOR EVERY TASK

1. **Read task**: `dstask <id> note`
2. **Check Part 2 exists** (auto-generated facts)
3. **YOU FILL Part 1** (your decisions)
4. **BOTH PARTS REQUIRED** before coding

## EXAMPLE

```bash
# Task: "Refactor parser to use functional composition"

PART 1 (CLAUDE FILLS):
  95/5: Use toolz.pipe, don't build pipeline
  DRY: Reuse BaseParser from parser.py:45
  SOLID: ONLY parse, not validate
  DDD: Layer=infrastructure
  TDD: tests/test_parser_functional.py, 95% coverage

PART 2 (AUTO-GENERATED):
  Research: "toolz recommended for functional composition"
  Duplicates: Found in parser.py:45, jsonl_parser.py:102
  Complexity: parser.py Score=C(11)
  Sizes: parser.py=251 lines (VIOLATION)
```

## ENFORCEMENT

- **ctask** generates Part 2 automatically
- **Claude** MUST fill Part 1 manually
- **Git hooks** block tasks without both parts
- **No coding** until both parts complete

## REMEMBER

Every future Claude session:
1. Will NOT remember this system
2. MUST read this file
3. MUST follow two-part structure
4. MUST fill Part 1 themselves

This prevents hallucination by separating:
- **Facts** (automated, real)
- **Decisions** (Claude-made, explicit)
