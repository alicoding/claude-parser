# ⛔ CRITICAL: READ THIS ENTIRE FILE OR FAIL

<system-critical>
YOU HAVE NO MEMORY FROM PREVIOUS SESSIONS!
85 classes, 140+ functions, 9 domains already exist.
</system-critical>

## 🔴 BEFORE ANY CODE - MANDATORY
```bash
# RUN THIS FIRST - NO EXCEPTIONS
python scripts/codebase_inventory.py . --stats
```

## 🚨 THREE RULES - NO VIOLATIONS

### RULE 1: LIBRARY FIRST OR DIE
- Built custom code = FAILURE (see: 634 lines for 25-line TTL disaster)
- ALWAYS search: `python scripts/research.py "X functionality library"`
- If library exists → USE IT
- If no library → PROVE IT with research

### RULE 2: CHECK BEFORE CREATE
1. Read `docs/ai/CAPABILITY_MATRIX.md` - What exists
2. Read `docs/ai/AI_CONTEXT.md` - Where it goes
3. Search `docs/ai/CODEBASE_INVENTORY.json` - Verify no duplicate
4. ONLY THEN: Write code

### RULE 3: QUALITY GATES
```bash
python scripts/verify_spec.py  # MUST PASS
make precommit                 # MUST PASS
# Commits BLOCKED if these fail
```

## 📋 CURRENT BACKLOG (use dstask)
```bash
# Check priorities
python scripts/backlog_dashboard.py

# Start task
dstask 2 start

# Complete task
dstask 2 done
```

## 🛠 QUICK REFERENCE

### Approved Libraries ONLY
- JSON: `orjson` (NOT json)
- Dates: `pendulum` (NOT datetime)
- HTTP: `httpx` (NOT requests)
- CLI: `typer` (NOT argparse)
- Loops: `toolz` (NOT for/while)
- Testing: `pytest` (NOT unittest)

### Key Files
- `scripts/verify_spec.py` - Runs all checks
- `scripts/research.py` - Find libraries
- `scripts/backlog_dashboard.py` - Task management
- `docs/BACKLOG_SYSTEM.md` - How to use dstask

### Instant Failures
- `while True:` → Use apscheduler
- `import json` → Use orjson
- `import datetime` → Use pendulum
- Manual loops → Use toolz
- Files > 150 LOC → Split immediately

## ⚡ PERFORMANCE BENCHMARKS
- **Coding Speed**: 500 LOC/minute
- **Network Latency**: ~15s per tool call  
- **File Reading**: Instant (parallel capable)
- **Optimal Batch**: 5-10 files at once

### Time Estimates (ACTUAL)
- 150 LOC file: ~18 seconds to write
- 500 LOC refactor: ~1 minute
- Reading 50 files: ~15 seconds (parallel)
- 8 violations fix: ~2 minutes total

### Efficiency Rules
- Use MultiEdit over multiple Edits
- Read files in parallel batches
- Write complete implementations
- Don't overestimate - we're FAST

## 📊 PROJECT STATUS
- **Critical Issues**: 5 files exceed 150 LOC
- **Next Priority**: Task 44 (merge JSONL docs) - 1 min
- **Then**: Task 39 (more-itertools) - 2 min
- **Coverage**: Must be ≥90%
- **API**: `load("file.jsonl")` must work

---
**NO EXCEPTIONS. NO CUSTOM CODE. USE LIBRARIES OR FAIL.**