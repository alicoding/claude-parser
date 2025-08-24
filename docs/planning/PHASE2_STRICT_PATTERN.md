# Phase 2: Strict Development Pattern

## 🎯 The Pattern We MUST Follow

### 1. Research First (95/5 Library Selection)
```python
# Use library_research.py BEFORE choosing any library
python library_research.py -t "topic" -q "specific questions"
```
- ✅ Example: We researched testing setup, found pytest-asyncio was the issue
- ❌ Never: Just pick a library without research

### 2. Design First (API Contract)
```markdown
# Write complete API design BEFORE any implementation
- Function signatures
- Input/output types  
- Error handling
- Success criteria
```
- ✅ Example: PHASE2_API_DESIGN.md defines everything upfront
- ❌ Never: Start coding without full API design

### 3. TDD Strictly (Red → Green → Refactor)
```python
# Step 1: Write failing tests (Red)
def test_feature():
    from module import function  # Will fail
    assert function() == expected

# Step 2: Minimal implementation (Green)
def function():
    return expected  # Just enough to pass

# Step 3: Refactor if needed (maintaining Green)
def function():
    # Clean implementation
```
- ✅ Example: Wrote 9 HookData tests first, then implemented model
- ❌ Never: Write implementation before tests

### 4. Validate Against Principles
```markdown
For EVERY implementation:
□ 95/5: Is the simple case 3 lines or less?
□ SOLID: Does each function do ONE thing?
□ DRY: Is there any duplication?
□ DDD: Are domain boundaries clear?
□ Library-First: Are we using the best library?
```
- ✅ Example: Single HookData model (DRY), not 8 classes
- ❌ Never: Compromise on principles for speed

### 5. Zero Technical Debt
```bash
# After EVERY commit, run:
grep -r "TODO\|FIXME\|HACK" --include="*.py" .
pytest tests/test_phase2/ -v --cov=claude_parser.hooks
mypy claude_parser/hooks --strict
ruff check claude_parser/hooks
```
- ✅ Example: All tests must pass, 100% coverage
- ❌ Never: Leave TODO comments or skip tests

---

## 📋 Checklist for Each Feature

### Before Starting
- [ ] Research libraries if needed (library_research.py)
- [ ] Write API design in markdown
- [ ] Get validation of design against principles
- [ ] Create test file with all test cases

### During Implementation  
- [ ] Write ONE test at a time
- [ ] Run test - verify it FAILS
- [ ] Write MINIMAL code to pass
- [ ] Run test - verify it PASSES
- [ ] Refactor if needed (tests still pass)
- [ ] Check complexity < 5 per function

### After Implementation
- [ ] All tests pass (100%)
- [ ] Coverage 100% for new code
- [ ] No TODO/FIXME/HACK comments
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] Run quality checks

---

## 🔄 Current Pattern Application

### ✅ HookData Model (Completed)
1. **Research**: ✅ Researched pydantic best practices
2. **Design**: ✅ Single model for all hooks (DRY)
3. **TDD**: ✅ 9 tests written first, then implementation
4. **Validation**: ✅ Meets all principles
5. **Zero Debt**: ✅ 100% tests pass, no TODOs

### 🔄 hook_input() Function (Next)
1. **Research**: Check if we need any special stdin handling
2. **Design**: Already defined in API design
3. **TDD**: Write tests for:
   - Valid JSON parsing
   - Invalid JSON handling  
   - Missing fields handling
   - All 8 hook types
   - Performance < 10ms
4. **Implementation**: Minimal code using orjson
5. **Validation**: Must be ≤ 10 lines of code

### 🔄 Exit Helpers (After hook_input)
1. **Research**: Best practice for sys.exit in libraries
2. **Design**: Already defined (3 functions)
3. **TDD**: Write tests for:
   - Exit codes (0, 1, 2)
   - stdout/stderr routing
   - Message handling
4. **Implementation**: Each function ≤ 3 lines
5. **Validation**: Must be simple enough for 95% use

---

## 📊 Quality Metrics We Track

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | 100% | 100% (models) |
| Complexity | < 5 | ✅ All < 5 |
| API Surface | ≤ 4 functions | 3 functions |
| 95% Use Case | ≤ 3 lines | 3 lines |
| Dependencies | Minimal | orjson, pydantic |
| Technical Debt | 0 | 0 |

---

## 🚫 Anti-Patterns to Avoid

### Code Smells We Reject
```python
# ❌ Multiple classes for similar things
class PreToolUseHook: ...
class PostToolUseHook: ...

# ❌ Complex initialization
hook = HookParser()
hook.configure(...)
hook.parse(...)

# ❌ Manual parsing
try:
    data = json.loads(stdin)
    if "field" in data:
        value = data["field"]
except:
    value = None

# ❌ Nested complexity
if condition1:
    if condition2:
        if condition3:
            do_something()
```

### What We Do Instead
```python
# ✅ Single model
class HookData: ...

# ✅ Zero configuration
data = hook_input()

# ✅ Library handles parsing
data = HookData(**orjson.loads(stdin))

# ✅ Flat, simple logic
if not condition: exit_error()
do_something()
```

---

## 🎯 Success Criteria

Before moving to next step, we MUST have:

1. **Tests**: All passing, 100% coverage
2. **Performance**: < 10ms for operations
3. **Simplicity**: 95% case in ≤ 3 lines
4. **Documentation**: Complete with examples
5. **Quality**: Zero linting/type errors
6. **Principles**: All 5 followed strictly

---

## 📝 The Contract

**We commit to:**
- Never skip research when choosing libraries
- Never write code before tests
- Never compromise on principles
- Never leave technical debt
- Never exceed complexity limits

**This pattern ensures:**
- Robustness through testing
- Maintainability through simplicity
- Performance through right libraries
- Quality through automation
- Success through discipline