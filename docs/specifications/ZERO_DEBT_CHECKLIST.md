# Zero Technical Debt Checklist

## 🎯 Our Commitment
**ZERO** technical debt, **ZERO** bugs, **100%** principle compliance.
This checklist ensures we deliver production-ready code to your projects.

---

## ✅ Per-Commit Checklist

### Before Writing Code
- [ ] Test written FIRST (TDD)
- [ ] Test is FAILING
- [ ] Test covers edge cases
- [ ] Test names describe behavior

### While Writing Code
- [ ] Minimal code to pass test
- [ ] No TODO/FIXME/HACK comments
- [ ] No commented-out code
- [ ] No `type: ignore`
- [ ] Complexity < 5 per function

### After Writing Code
- [ ] All tests pass (not just new ones)
- [ ] Coverage still 100%
- [ ] No new warnings
- [ ] Documentation updated

---

## 🔍 Automated Checks

```bash
#!/bin/bash
# zero_debt_check.sh - Run after EVERY change

echo "🔍 Checking for Technical Debt..."

# 1. No TODO/FIXME/HACK
if grep -r "TODO\|FIXME\|HACK" --include="*.py" .; then
    echo "❌ Found TODO/FIXME/HACK comments"
    exit 1
fi

# 2. No skipped tests
if grep -r "@pytest.mark.skip\|@skip" tests/; then
    echo "❌ Found skipped tests"
    exit 1
fi

# 3. No commented code
if grep -r "^\s*#.*def \|^\s*#.*class " --include="*.py" .; then
    echo "❌ Found commented code"
    exit 1
fi

# 4. No type ignores
if grep -r "type: ignore" --include="*.py" .; then
    echo "❌ Found type: ignore"
    exit 1
fi

# 5. Test coverage 100%
coverage run -m pytest
coverage report --fail-under=100

# 6. Type checking passes
mypy . --strict

# 7. Complexity check
radon cc . -s -nb

# 8. No print statements (use logger)
if grep -r "^[^#]*print(" --include="*.py" claude_parser/; then
    echo "❌ Found print statements (use logger)"
    exit 1
fi

echo "✅ ZERO TECHNICAL DEBT - Ready to ship!"
```

---

## 📊 SOLID Compliance Check

### Single Responsibility
```python
def check_single_responsibility():
    """Each class/function does ONE thing."""
    
    # Function should have single clear purpose
    assert len(function.__doc__.split('\n')[0]) < 80
    
    # Class should have single reason to change
    assert len(class_methods) < 7  # 7±2 rule
```

### Open/Closed
```python
def check_open_closed():
    """Open for extension, closed for modification."""
    
    # No isinstance() checks in 95% API
    assert "isinstance" not in basic_api_code
    
    # Extensions via composition, not inheritance
    assert BaseClass.__subclasses__() == []
```

### Liskov Substitution
```python
def check_liskov():
    """All hooks work with same interface."""
    
    for hook_type in ALL_HOOK_TYPES:
        data = hook_input()  # Same function works
        exit_success()       # Same exit works
```

### Interface Segregation
```python
def check_interface_segregation():
    """Minimal required interfaces."""
    
    # 95% API has only 3 functions
    assert len(basic_api_functions) == 3
    
    # Advanced features are separate
    assert "json_output" not in basic_api
```

### Dependency Inversion
```python
def check_dependency_inversion():
    """Depend on abstractions, not concretions."""
    
    # Optional dependencies
    assert "watchfiles" not in required_dependencies
    
    # Abstractions (protocols/interfaces) used
    assert uses_protocols == True
```

---

## 🔄 DRY Compliance Check

```python
def check_dry_compliance():
    """Don't Repeat Yourself."""
    
    # Single HookData model for all types
    assert count(HookDataClasses) == 1
    
    # No duplicate parsing logic
    assert count(json_parse_functions) == 1
    
    # No duplicate error handling
    assert count(try_except_patterns) < 5
```

---

## 📦 DDD Compliance Check

```python
def check_ddd_compliance():
    """Domain-Driven Design."""
    
    # Clear bounded contexts
    assert "hooks" not in "watch" module
    assert "watch" not in "hooks" module
    
    # Domain models are immutable
    assert HookData.Config.frozen == True
    
    # Aggregates own their domain
    assert ConversationMonitor.owns(file_watching)
```

---

## 🧪 TDD Compliance Check

```python
def check_tdd_compliance():
    """Test-Driven Development."""
    
    # Tests exist for all code
    assert coverage == 100
    
    # Tests were written first (git history)
    assert test_commit.before(implementation_commit)
    
    # Tests are meaningful
    assert "test_" in test_name
    assert test_has_assertion == True
```

---

## 📐 95/5 Compliance Check

```python
def check_95_5_compliance():
    """95% simple, 5% powerful."""
    
    # 95% use case in 3 lines
    from claude_parser.hooks import hook_input, exit_success, exit_block
    data = hook_input()
    if data.tool_name == "Write": exit_block("No")
    exit_success()
    
    # Advanced features are optional
    try:
        from claude_parser.hooks import advanced
    except ImportError:
        pass  # Should work without it
```

---

## 🚀 Pre-Release Checklist

### Code Quality
- [ ] All tests pass
- [ ] Coverage = 100%
- [ ] Zero TODO/FIXME/HACK
- [ ] Zero skipped tests
- [ ] Zero type ignores
- [ ] Complexity < 5
- [ ] No print statements

### Documentation
- [ ] All public functions documented
- [ ] Examples for 95% use cases
- [ ] Migration guide from alternatives
- [ ] API reference complete

### Performance
- [ ] Hook parsing < 10ms
- [ ] File watching < 100ms
- [ ] Memory usage constant
- [ ] No memory leaks

### Security
- [ ] Input validation complete
- [ ] No path traversal
- [ ] No code injection
- [ ] Errors don't leak info

### Integration
- [ ] Works with real Claude hooks
- [ ] Works with real transcripts
- [ ] Error handling graceful
- [ ] Cross-platform tested

---

## 📝 Sign-Off

Before releasing to your projects:

```python
def ready_for_production():
    """Final check before release."""
    
    assert technical_debt == 0
    assert test_coverage == 100
    assert principles_followed == "ALL"
    assert api_lines_for_95_percent <= 3
    
    print("✅ Ready for production!")
    print("✅ Ready for open source!")
    print("✅ Zero technical debt achieved!")
    
    return True
```

**Developer Sign-off**: ________________
**Date**: ________________
**Version**: 2.0.0

---

## 🎯 The Promise

This code will:
1. Work in your hook-v2 project (3 lines)
2. Work in your memory project (1 line)
3. Have ZERO bugs
4. Have ZERO technical debt
5. Be the reference implementation for "doing it right"

**No compromises. No shortcuts. Just clean, solid code.**