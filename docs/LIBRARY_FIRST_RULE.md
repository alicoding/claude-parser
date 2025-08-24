# 🚨 MANDATORY: LIBRARY FIRST RULE

## THE PROBLEM
Claude's default behavior creates 600+ lines when 25 would work.
This document MUST be read before ANY implementation task.

## THE RULE: LIBRARY FIRST OR DIE

### Before ANY Code, You MUST:
1. **SEARCH**: "What library/framework already solves this?"
2. **RESEARCH**: Check PyPI, GitHub, Stack Overflow
3. **PROVE**: If claiming no library exists, show evidence
4. **USE**: If library exists, use it. NO CUSTOM CODE.

## REAL FAILURES (ACTUAL EXAMPLES)

| What Was Built | Lines Written | Should Have Used | Actual Lines Needed |
|----------------|---------------|------------------|-------------------|
| TTL Cleanup | 634 | apscheduler | 25 |
| Event System | 200+ | blinker | 5 |
| Retry Logic | 100+ | tenacity | 3 |
| Batch Processing | 80+ | more-itertools | 10 |
| Date Parsing | 50+ | pendulum | 2 |
| Async Scheduler | 150+ | arq/celery | 15 |
| Memory Project | 2,553 | Proper libraries | 200 |

## THE WORKFLOW (NO EXCEPTIONS)

```python
# CORRECT WORKFLOW:
1. Task: "Build X functionality"
2. STOP: "What library does X?"
3. Search: research.py "X functionality python library"
4. Found? Use it. END.
5. Not found? Prove it with links.

# WRONG WORKFLOW (INSTANT FAILURE):
1. Task: "Build X"
2. Start coding X
3. 600 lines later...
```

## BANNED PATTERNS (DELETE ON SIGHT)

```python
# ❌ NEVER WRITE
while True:
    await asyncio.sleep(86400)  # Use apscheduler!

# ❌ NEVER WRITE  
for i in range(0, len(items), batch_size):
    batch = items[i:i+batch_size]  # Use more-itertools.chunked!

# ❌ NEVER WRITE
try:
    operation()
except:
    retry()  # Use tenacity!

# ❌ NEVER WRITE
if event_type == "user_action":
    handle_event()  # Use blinker!
```

## APPROVED LIBRARIES (USE THESE FIRST)

| Need | Use This Library | NOT Custom Code |
|------|-----------------|-----------------|
| Scheduling | apscheduler | NOT while True |
| Events | blinker | NOT if/elif chains |
| Retry | tenacity | NOT try/except loops |
| Batch | more-itertools | NOT manual chunking |
| Dates | pendulum | NOT datetime parsing |
| Async Tasks | arq, celery | NOT asyncio.create_task |
| CLI | typer | NOT argparse |
| Validation | pydantic | NOT manual checks |
| HTTP | httpx | NOT urllib |
| Testing | pytest | NOT unittest |

## THE COST OF IGNORING THIS

- **Memory Project**: 2,553 lines → Should be 200 lines
- **TTL System**: 634 lines → Should be 25 lines  
- **Weeks of work** → Should be days
- **Unmaintainable mess** → Should be clean

## HOW TO USE THIS DOCUMENT

```bash
# In every request, add:
"Can we build X but read docs/LIBRARY_FIRST_RULE.md first"

# Or even shorter:
"Build X - LIBRARY FIRST RULE applies"
```

## THE NUCLEAR OPTION

If Claude starts writing custom code:
```
STOP! You're violating LIBRARY FIRST RULE.
What library does this? Search first.
```

## SUCCESS METRICS

✅ **Success**: 95% library code, 5% glue
❌ **Failure**: 95% custom code, 5% libraries

## REMEMBER

Every line of custom code is a failure to find the right library.
The best code is the code you don't write.
Someone already solved your problem - FIND THEIR LIBRARY.

---

**NO CUSTOM CODE IF A LIBRARY EXISTS. PERIOD.**