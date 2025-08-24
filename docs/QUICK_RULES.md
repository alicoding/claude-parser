# ⚡ QUICK REFERENCE: STOP CLAUDE FROM OVERENGINEERING

## THE ONE-LINER TO ADD TO EVERY REQUEST

```
"Read docs/LIBRARY_FIRST_RULE.md before any code"
```

## INSTANT STOP PHRASES (When Claude Goes Rogue)

```bash
# When you see Claude building custom code:
"STOP! What library does this?"

# When you see while True:
"STOP! Use apscheduler"

# When you see custom event handling:
"STOP! Use blinker"

# When you see manual retry:
"STOP! Use tenacity"

# When you see anything over 50 lines:
"STOP! This should be 5 lines with a library"
```

## THE MAGIC WORDS THAT WORK

✅ **WORKS:**
- "Find the library first"
- "What library already does this?"
- "Search PyPI before coding"
- "95/5 principle - library first"
- "No custom code if library exists"

❌ **DOESN'T WORK:**
- "Keep it simple" → Claude: *writes 600 lines*
- "Use libraries" → Claude: *builds custom anyway*
- "Don't reinvent" → Claude: *reinvents everything*

## EXAMPLE PROMPTS THAT PREVENT DISASTERS

### ❌ BAD (leads to 600 lines):
"Build a task scheduler"

### ✅ GOOD (leads to 5 lines):
"Build a task scheduler - find what library does this first"

### ❌ BAD:
"Add retry logic to this function"

### ✅ GOOD:
"Add retry logic - use tenacity library"

### ❌ BAD:
"Process these items in batches"

### ✅ GOOD:
"Process in batches - use more-itertools.chunked"

## THE CHECKLIST FOR EVERY TASK

Before coding ANYTHING:
- [ ] Did Claude search for existing libraries?
- [ ] Did Claude prove no library exists?
- [ ] Is the solution <50 lines?
- [ ] Is it 95% library usage?

If any answer is NO → STOP!

## QUICK LIBRARY LOOKUP

```python
# Instead of Claude building:
scheduler → apscheduler
events → blinker
retry → tenacity
batch → more-itertools
dates → pendulum
async → arq/celery
CLI → typer
validation → pydantic
```

---

**Remember: Every custom implementation is a failure to search properly.**