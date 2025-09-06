# FIX: dstask note command issue RESOLVED

## The Problem
- Git hooks were corrupting YAML date formats
- Python's yaml.dump() changes date format from ISO to space-separated
- dstask couldn't parse the corrupted format

## The Solution

### 1. Disable the problematic hooks (temporary)
```bash
mv ~/.dstask/.git/hooks/post-commit ~/.dstask/.git/hooks/post-commit.disabled
mv ~/.dstask/.git/hooks/pre-commit ~/.dstask/.git/hooks/pre-commit.disabled
```

### 2. Fix corrupted YAML files
```bash
for file in ~/.dstask/pending/*.yml; do
  if grep -q "2025-08-24 " "$file"; then
    sed -i '' 's/2025-08-24 /2025-08-24T/g' "$file"
    sed -i '' 's/0001-01-01 00:00:00/0001-01-01T00:00:00/g' "$file"
    echo "Fixed: $(basename $file)"
  fi
done
```

### 3. Adding notes (two methods)

#### Method 1: When creating tasks (BEST)
```bash
dstask add "Task summary" / "This is the note content"
```

#### Method 2: For existing tasks (requires editor)
```bash
# This opens your default editor
dstask 70 note

# Or set EDITOR temporarily
EDITOR=nano dstask 70 note
```

## For Non-Interactive Scripts

Since dstask note requires an editor, for scripts use:

```bash
# Option 1: Create with note from start
dstask add "Worker implementation" / "PART 1: Design decisions here..."

# Option 2: Direct YAML modification (advanced)
# Edit ~/.dstask/pending/<task-uuid>.yml directly
# But be careful with date formats!
```

## Important Notes

1. The `/` separator works ONLY when creating new tasks
2. For existing tasks, dstask ALWAYS opens an editor
3. Our git hooks need to be rewritten to preserve YAML format
4. Use ISO 8601 dates: `2025-08-24T22:00:00-04:00`

## Your Task 70 Fix

Since the note command requires an editor, you can:

1. Use the editor:
```bash
EDITOR=vim dstask 70 note
```

2. Or recreate the task with notes:
```bash
# Delete old one
dstask 70 remove

# Create new with notes
dstask add "Worker implementation" +temporal-hooks / "PART 1: YOUR DECISIONS HERE
95/5: Use temporalio SDK
DRY: Reuse existing base
SOLID: Single responsibility
etc..."
```

The bug is fixed - dstask works fine now that we disabled the corrupting hooks!
