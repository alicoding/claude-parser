# Incremental Fix Plan with Git Checkpoints

## Fix Order (Safest First)

Each fix will be:
1. Implemented
2. Tested
3. Committed
4. Validated for no regressions

## Fix #1: Test Constants (3 minutes)
**Risk: None - Only adds new module**

```bash
# Create constants module
cat > tests/constants.py << 'EOF'
"""Test constants to eliminate magic strings."""

class TestDefaults:
    SESSION_ID = 'test-session-001'
    TRANSCRIPT_PATH = '/tmp/test-transcript.jsonl'
    PROJECT_PATH = '/tmp/test-project'
    TIMESTAMP = '2025-01-01T00:00:00.000Z'
EOF

# Test it works
poetry run python -c "from tests.constants import TestDefaults; print(TestDefaults.SESSION_ID)"

# Commit
git add tests/constants.py
git commit -m "refactor: Add test constants module (Fix 1/10)

- Eliminates magic strings
- No existing code modified
- Zero breaking changes"
```

## Fix #2: Replace One Magic String (3 minutes)
**Risk: Low - Single file change**

```bash
# Replace in one test file first
sed -i '' "s/'abc123'/TestDefaults.SESSION_ID/g" tests/test_phase2/test_hook_models.py

# Add import
sed -i '' '1i\
from tests.constants import TestDefaults
' tests/test_phase2/test_hook_models.py

# Test
poetry run pytest tests/test_phase2/test_hook_models.py -xvs

# Commit
git add tests/test_phase2/test_hook_models.py
git commit -m "refactor: Replace magic strings in hook_models test (Fix 2/10)

- Uses TestDefaults.SESSION_ID
- Tests still pass
- No API changes"
```

## Fix #3: Test Factory for One Tool (3 minutes)
**Risk: Low - Adds factory, doesn't change existing**

```bash
# Add to test_factories.py the create_tool_response_test function

# Test it
poetry run python -c "
from tests.test_factories import HookTestFactory
test = HookTestFactory.create_tool_response_test('LS', 'output')
test()  # Should work
"

# Commit
git add tests/test_factories.py
git commit -m "refactor: Add test factory for tool responses (Fix 3/10)

- Reduces duplication
- Original tests unchanged
- Factory available for future use"
```

## Fix #4: File Processor Class (6 minutes)
**Risk: Medium - But wrapped in backward compatible function**

```bash
# Create file processor
cat > claude_parser/patterns/file_processor.py << 'EOF'
"""File processor to eliminate duplication."""
from pathlib import Path
from toolz import pipe
from toolz.curried import filter as toolz_filter

class FileProcessor:
    def __init__(self, patterns: list, exclusions: list):
        self.patterns = patterns
        self.exclusions = exclusions

    def process(self, base_path: str) -> list:
        if not Path(base_path).exists():
            return []
        files = []
        for pattern in self.patterns:
            files.extend(Path(base_path).rglob(pattern))
        return list(toolz_filter(
            lambda p: not any(exc in str(p) for exc in self.exclusions),
            files
        ))
EOF

# Update verify_spec_v2.py to use it
# But keep original function signature

# Test
poetry run python scripts/verify_spec_v2.py

# Commit
git add claude_parser/patterns/file_processor.py scripts/verify_spec_v2.py
git commit -m "refactor: Add FileProcessor to reduce duplication (Fix 4/10)

- Extracts repeated file processing logic
- Original functions still work
- DRY principle applied"
```

## Fix #5: Conversation Delegates (9 minutes)
**Risk: High - Core entity change**

```bash
# Create delegates module
cat > claude_parser/patterns/delegates.py << 'EOF'
"""Delegates for Conversation to avoid God Object."""
from typing import List
from toolz import filter as toolz_filter

class MessageQueryDelegate:
    def __init__(self, messages):
        self._messages = messages

    def filter(self, predicate):
        return list(toolz_filter(predicate, self._messages))

    def search(self, query: str, case_sensitive: bool = False):
        if case_sensitive:
            return self.filter(lambda m: query in m.text_content)
        return self.filter(lambda m: query.lower() in m.text_content.lower())
EOF

# Update Conversation to use delegate internally
# But keep all public methods

# Test thoroughly
poetry run pytest tests/test_conversation.py -xvs
poetry run pytest tests/test_ddd_conversation.py -xvs

# Commit
git add claude_parser/patterns/delegates.py claude_parser/domain/entities/conversation.py
git commit -m "refactor: Add delegation to Conversation (Fix 5/10)

- Fixes God Object antipattern
- All public APIs unchanged
- Internal delegation for cleaner code"
```

## Fix #6: Test Mixins (6 minutes)
**Risk: Low - Only affects test organization**

```bash
# Create mixins
cat > tests/utilities/mixins.py << 'EOF'
"""Test mixins for single responsibility."""

class MetadataTestMixin:
    def assert_metadata_valid(self, conv):
        assert conv.metadata is not None
        assert hasattr(conv.metadata, 'session_id')

class ComplianceTestMixin:
    def assert_uses_orjson(self, module):
        assert 'json' not in str(module.__dict__)
EOF

# Update test classes to use mixins
# Original tests remain

# Test
poetry run pytest tests/ -x

# Commit
git add tests/utilities/mixins.py tests/test_*.py
git commit -m "refactor: Add test mixins for SRP (Fix 6/10)

- Splits test responsibilities
- Original test methods intact
- Improved maintainability"
```

## Validation After Each Fix

```python
# scripts/validate_fix.py
"""Validate each fix doesn't break anything."""

import orjson
from pathlib import Path
import subprocess
import sys

def validate_fix(fix_number: int):
    """Ensure fix didn't break anything."""

    # Load baseline
    baseline = orjson.loads(Path("baseline.json").read_bytes())

    # Run tests
    result = subprocess.run(
        "poetry run pytest tests/ -x -q",
        shell=True, capture_output=True
    )

    if result.returncode != 0:
        print(f"❌ Fix {fix_number} broke tests!")
        print("Run: git reset --hard HEAD~1")
        return False

    # Check API compatibility
    from claude_parser.domain.entities.conversation import Conversation
    conv_methods = [m for m in dir(Conversation) if not m.startswith('_')]
    baseline_methods = baseline['apis']['Conversation']['methods']

    if set(baseline_methods) - set(conv_methods):
        print(f"❌ Fix {fix_number} removed API methods!")
        return False

    print(f"✅ Fix {fix_number} validated - no regressions")
    return True

if __name__ == "__main__":
    fix_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    if not validate_fix(fix_num):
        sys.exit(1)
```

## Git Checkpoint Commands

```bash
# After each successful fix
git tag fix-1-complete
git tag fix-2-complete
# ... etc

# If something breaks
git reset --hard fix-3-complete  # Go back to last good state

# View progress
git log --oneline --graph --decorate

# Push incrementally
git push origin main --tags
```

## Complete Incremental Timeline

| Fix # | Description | Time | Risk | Git Tag |
|-------|------------|------|------|---------|
| 1 | Test constants | 3 min | None | fix-1-complete |
| 2 | Replace one magic string | 3 min | Low | fix-2-complete |
| 3 | Test factory | 3 min | Low | fix-3-complete |
| 4 | File processor | 6 min | Medium | fix-4-complete |
| 5 | Conversation delegates | 9 min | High | fix-5-complete |
| 6 | Test mixins | 6 min | Low | fix-6-complete |
| 7 | Replace remaining magic strings | 9 min | Low | fix-7-complete |
| 8 | Fix remaining DRY violations | 12 min | Medium | fix-8-complete |
| 9 | Fix remaining SOLID violations | 12 min | Medium | fix-9-complete |
| 10 | Final cleanup | 6 min | Low | fix-10-complete |
| **Total** | **All violations fixed** | **69 min** | - | refactor-complete |

## Safety Rollback at Any Point

```bash
# Check current state
python scripts/validate_fix.py 5  # After fix 5

# If broken, rollback
git reset --hard fix-4-complete

# Or use reflog
git reflog
git reset --hard HEAD@{2}
```

## Final Validation

```bash
# After all fixes
python scripts/detect_new_violations.py
# Should show: 18 violations → 0 violations

# Run full test suite
poetry run pytest tests/ --cov=claude_parser --cov-fail-under=90

# Check performance
poetry run pytest tests/test_zero_regression.py -xvs

# If all good
git tag refactor-complete
git push origin main --tags
```

This incremental approach ensures:
1. ✅ Each fix is isolated and tested
2. ✅ Git commits after every change
3. ✅ Can rollback at any point
4. ✅ No "big bang" refactoring
5. ✅ Total time: ~70 minutes
6. ✅ Complete audit trail in git history
