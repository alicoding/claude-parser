# Microcontext for Claude Parser

## 🚨 ACTIVE RULES (Read EVERY time)
- Backlog first: `dstask <id> show`
- Research thread: Use `scripts/research.py`
- <150 LOC per file MAX
- 95% library, 5% glue
- claude-parser is JUST a parsing library (NO events, NO blinker)

## Libraries (NO alternatives)
- JSON: orjson (NEVER json)
- Dates: pendulum (NEVER datetime)
- HTTP: httpx (NEVER requests)
- CLI: typer (NEVER argparse)
- Functional: toolz (NEVER loops)
- Validation: pydantic
- Testing: pytest

## Patterns ONLY
```python
# Self-documenting models
class Message(BaseModel):
    field: str = Field(..., description="Shows in IDE")
    
# Functional operations
from toolz import pipe, map, filter
result = pipe(data, map(transform), filter(validate))
```

## FORBIDDEN
- Manual loops (use toolz)
- json/datetime imports
- Custom parsing (use pydantic)
- Separate docs (use docstrings)
- New tasks (update existing)
- Assumptions (check backlog)

## When stuck
- Check: `dstask 50 show` (WORKFLOW PRINCIPLES)
- Research: `python scripts/research.py "library for X"`
- Verify: `python scripts/verify_spec.py`