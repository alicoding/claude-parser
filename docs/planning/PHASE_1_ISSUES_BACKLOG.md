# Phase 1 - Known Issues Backlog

## CRITICAL: Must Fix Before Phase 2

All issues must be resolved with TDD approach: Write failing test → Fix implementation → Verify test passes.

### ISSUE-001: Tool Use Messages Not Parsing (HIGH PRIORITY)
**Problem**: Integration test shows 0 tool uses in 3,105 message file (impossible)
**Impact**: Core functionality broken, violates contract
**Root Cause**: Models don't match actual Claude JSONL tool format
**TDD Approach**:
1. Write test with real tool use message from JSONL
2. Test should fail (proving issue exists)
3. Fix models to handle actual format
4. Verify test passes

**Acceptance Criteria**:
- [ ] Extract and examine 5 real tool use messages from JSONL
- [ ] Write failing test that expects tool uses to be found
- [ ] Update models to match actual structure
- [ ] Integration test shows >0 tool uses
- [ ] All existing tests still pass

### ISSUE-002: Message Content Structure Inconsistency (HIGH PRIORITY)
**Problem**: Some messages use `content` field, others use `message.content` structure
**Impact**: Text extraction may miss content, search functionality incomplete
**Violates**: DRY principle (multiple content extraction methods)
**TDD Approach**:
1. Write test with various content structures from real JSONL
2. Test should fail for inconsistent extraction
3. Implement unified content extraction strategy
4. All content extraction tests pass

**Acceptance Criteria**:
- [ ] Document all content structures found in real JSONL
- [ ] Write comprehensive content extraction tests
- [ ] Implement single, unified content extraction method
- [ ] All messages return correct text_content
- [ ] Search functionality works across all message types

### ISSUE-003: Missing psutil Dependency (MEDIUM PRIORITY)
**Problem**: Memory test fails due to missing dependency
**Impact**: Incomplete test coverage, can't verify performance requirements
**Violates**: 95/5 principle (tooling should just work)
**TDD Approach**:
1. Test currently fails
2. Add psutil dependency
3. Test should pass

**Acceptance Criteria**:
- [ ] Add psutil to dev dependencies
- [ ] Memory test passes
- [ ] Performance benchmarks work
- [ ] No new dependency conflicts

### ISSUE-004: Project Structure Conflicts (MEDIUM PRIORITY)  
**Problem**: Old test files in packages/ directory conflict with pytest
**Impact**: `pytest` without path specification fails
**Violates**: Clean code principles
**TDD Approach**:
1. Verify current pytest run fails without explicit path
2. Clean up conflicting files
3. Verify pytest runs cleanly from root

**Acceptance Criteria**:
- [ ] `poetry run pytest` works from project root
- [ ] No ImportError or ModuleNotFoundError
- [ ] All our tests still pass
- [ ] Clean project structure

### ISSUE-005: No Claude Format Validation (LOW PRIORITY)
**Problem**: Parser accepts any JSONL, doesn't validate Claude Code format
**Impact**: Could parse non-Claude files incorrectly
**Violates**: 95/5 principle (should fail fast on wrong input)
**TDD Approach**:
1. Write test with non-Claude JSONL
2. Test should expect validation error
3. Add Claude format detection
4. Test passes with proper error

**Acceptance Criteria**:
- [ ] Define Claude JSONL format signature
- [ ] Write validation tests
- [ ] Add optional strict mode validation
- [ ] Helpful error messages for wrong format

## Resolution Order (TDD Workflow)

### Step 1: Investigation Phase
```bash
# Examine real data to understand issues
cd /Users/ali/.claude/projects/claude-parser
PYTHONPATH=. python3 -c "
from claude_parser.parser import parse_jsonl_streaming
import json
count = 0
for msg in parse_jsonl_streaming('path_to_real.jsonl'):
    if 'tool' in msg.get('type', '').lower():
        print(f'TOOL MESSAGE: {json.dumps(msg, indent=2)}')
        count += 1
        if count >= 3: break
"
```

### Step 2: Write Failing Tests
Create test files that demonstrate each issue:
- `test_tool_use_real_format.py` - Should fail initially
- `test_content_extraction_comprehensive.py` - Should fail initially  
- `test_memory_performance.py` - Currently fails
- `test_project_structure.py` - Should fail initially
- `test_claude_format_validation.py` - Should fail initially

### Step 3: Fix Implementation
Follow TDD cycle for each issue:
1. Red: Write failing test
2. Green: Minimal fix to make test pass
3. Refactor: Clean up while keeping tests green

### Step 4: Verification
```bash
# All tests must pass before Phase 2
poetry run pytest tests/ -v
poetry run mypy claude_parser
poetry run ruff check claude_parser
```

## Definition of Done for Phase 1

**Phase 1 is NOT complete until**:
- [ ] All 5 issues resolved
- [ ] All tests passing (no failures, no skips)
- [ ] Integration test shows realistic tool use count
- [ ] Memory performance test passes
- [ ] `pytest` runs clean from root
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Real JSONL parsing works 100%

## Next Session Action Plan

1. **Start with ISSUE-001** (highest impact)
2. **Follow strict TDD** - failing test first, then fix
3. **One issue at a time** - complete before moving to next
4. **Update this backlog** as issues are resolved
5. **Only proceed to Phase 2** when all issues are ✅

---
*No shortcuts. No partial fixes. 100% quality before moving forward.*