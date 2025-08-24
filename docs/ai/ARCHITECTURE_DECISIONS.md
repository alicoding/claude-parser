# Architecture Decision Records (ADRs)

## ADR-001: 95/5 Library-First Architecture

### Status
Accepted

### Context
Custom code is a liability. Every line we write is a bug waiting to happen, a test to maintain, and knowledge to transfer.

### Decision
- Use existing libraries for 95% of functionality
- Write only 5% glue code to connect libraries
- NEVER implement what a library already does

### Consequences
- ✅ Reduced bugs (libraries are battle-tested)
- ✅ Faster development (no reinventing wheels)
- ✅ Better performance (libraries are optimized)
- ❌ More dependencies to manage
- ❌ Need to learn library APIs

### Examples
- Use `orjson` not `json` (3x faster)
- Use `pendulum` not `datetime` (better timezone handling)
- Use `toolz` not manual loops (functional programming)

---

## ADR-002: Domain-Driven Design Structure

### Status
Accepted

### Context
Codebases become unmaintainable when business logic mixes with infrastructure.

### Decision
Organize code by domain boundaries:
- `models/` - Domain entities and value objects
- `domain/` - Business logic and rules
- `application/` - Use cases and orchestration
- `infrastructure/` - Technical details

### Consequences
- ✅ Clear separation of concerns
- ✅ Easy to find code
- ✅ Testable business logic
- ❌ More directories to navigate
- ❌ Need to understand DDD concepts

---

## ADR-003: Functional Programming with Toolz

### Status
Accepted

### Context
Manual loops and imperative code lead to bugs and are hard to test.

### Decision
- Use `toolz` for all data transformations
- Prefer `map`, `filter`, `reduce` over loops
- Use `pipe` for function composition
- Make functions pure when possible

### Consequences
- ✅ More readable code
- ✅ Easier to test
- ✅ Less state bugs
- ❌ Learning curve for functional style
- ❌ Can be less intuitive initially

### Example
```python
# Bad - Manual loop
results = []
for item in items:
    if item.is_valid():
        results.append(transform(item))

# Good - Functional
from toolz import pipe, filter, map
results = pipe(
    items,
    lambda x: filter(lambda i: i.is_valid(), x),
    lambda x: map(transform, x),
    list
)
```

---

## ADR-004: Pydantic for All Models

### Status
Accepted

### Context
Data validation is critical but manual validation is error-prone.

### Decision
- ALL models must use Pydantic
- Use type hints everywhere
- Let Pydantic handle validation
- Use Pydantic settings for configuration

### Consequences
- ✅ Automatic validation
- ✅ Clear data contracts
- ✅ JSON schema generation
- ❌ Slightly slower than plain classes
- ❌ Need to learn Pydantic

---

## ADR-005: Test-Driven Development (TDD)

### Status
Accepted

### Context
Code without tests is broken by design.

### Decision
- Write tests BEFORE implementation
- Minimum 90% coverage (enforced)
- New code needs 100% coverage
- Use real Claude JSONL files for integration tests

### Consequences
- ✅ Fewer bugs in production
- ✅ Safe refactoring
- ✅ Living documentation
- ❌ Slower initial development
- ❌ Need to maintain tests

---

## ADR-006: Single Source of Truth

### Status
Accepted

### Context
Duplicate code leads to inconsistent bug fixes and maintenance nightmares.

### Decision
- Each concept has ONE implementation
- Shared utilities in `infrastructure/`
- No copy-paste programming
- DRY (Don't Repeat Yourself) strictly enforced

### Consequences
- ✅ Consistent behavior
- ✅ Single place to fix bugs
- ✅ Easier maintenance
- ❌ Need to find existing code first
- ❌ Can create tight coupling

### Example
File operations are ONLY in `infrastructure/file_utils.py`

---

## ADR-007: Explicit Over Implicit

### Status
Accepted

### Context
Magic and implicit behavior makes code hard to understand and debug.

### Decision
- No monkey patching
- No global state
- Explicit imports (no `from x import *`)
- Clear function names
- Type hints everywhere

### Consequences
- ✅ Code is self-documenting
- ✅ Easier debugging
- ✅ Better IDE support
- ❌ More verbose
- ❌ More typing required

---

## ADR-008: Feature Registry for Capability Tracking

### Status
Accepted

### Context
Without tracking what's implemented, we risk duplicate work and incomplete features.

### Decision
- Maintain feature registry in `features/`
- Track status: complete, partial, planned
- Update registry when adding features
- Use registry to prevent duplication

### Consequences
- ✅ Clear implementation status
- ✅ Prevents duplicate work
- ✅ Good for documentation
- ❌ Extra maintenance overhead
- ❌ Can become outdated

---

## ADR-009: File Size Limits (150 LOC)

### Status
Accepted

### Context
Large files are hard to understand, test, and maintain.

### Decision
- Maximum 150 lines per file
- Enforced by pre-commit hooks
- Split large files by responsibility
- Follow Single Responsibility Principle

### Consequences
- ✅ More maintainable code
- ✅ Easier to understand
- ✅ Better git diffs
- ❌ More files to manage
- ❌ Need to think about organization

---

## ADR-010: Hierarchical JSON for AI Context

### Status
Accepted

### Context
AI assistants need structured context to avoid hallucination and wrong placements.

### Decision
- Generate codebase inventory as hierarchical JSON
- Group by domain/responsibility
- Include all metadata (functions, classes, etc.)
- Auto-generate with AST analysis

### Consequences
- ✅ AI has full context awareness
- ✅ Prevents duplicate implementations
- ✅ Ensures correct file placement
- ❌ Need to regenerate on changes
- ❌ Large context files

### Implementation
Run `python scripts/codebase_inventory.py` to generate

---

## ADR-011: No Backward Compatibility Debt

### Status
Accepted

### Context
Maintaining backward compatibility for unused features creates technical debt.

### Decision
- Remove deprecated code immediately
- No compatibility shims
- Clean breaks when refactoring
- Document breaking changes

### Consequences
- ✅ Cleaner codebase
- ✅ Less maintenance burden
- ✅ Faster development
- ❌ Can break existing users
- ❌ Need clear migration paths

---

## ADR-012: Library Choices Are Final

### Status
Accepted

### Context
Switching libraries mid-project causes inconsistency and wasted effort.

### Decision
Libraries in SPECIFICATION.md are mandatory:
- `orjson` for JSON (NOT json)
- `pendulum` for dates (NOT datetime)
- `httpx` for HTTP (NOT requests)
- `typer` for CLI (NOT argparse)
- `pytest` for tests (NOT unittest)

### Consequences
- ✅ Consistent codebase
- ✅ No decision fatigue
- ✅ Known performance characteristics
- ❌ Locked into choices
- ❌ Can't use alternatives

---

## ADR-013: Real Data for Testing

### Status
Accepted

### Context
Tests with mock data don't catch real-world edge cases.

### Decision
- Use actual Claude JSONL files for tests
- Test with various file sizes
- Include edge cases from real usage
- Located in `~/.claude/projects/`

### Consequences
- ✅ Catch real bugs
- ✅ Handle actual format variations
- ✅ Better confidence
- ❌ Tests depend on file system
- ❌ Slower test execution

---

## ADR-014: Hooks for Enforcement

### Status
Accepted

### Context
Code quality rules are useless if not enforced.

### Decision
- Pre-commit hooks block violations
- CI/CD enforces on every push
- No way to bypass checks
- Automated fixes where possible

### Consequences
- ✅ Consistent quality
- ✅ No accidental violations
- ✅ Self-enforcing standards
- ❌ Can slow down commits
- ❌ Need to fix issues immediately

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

### Status
[Proposed | Accepted | Deprecated | Superseded]

### Context
[Why we need this decision]

### Decision
[What we decided]

### Consequences
- ✅ [Positive consequence]
- ❌ [Negative consequence]
```