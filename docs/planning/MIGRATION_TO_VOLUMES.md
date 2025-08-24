# Migration Checklist: Moving to /Volumes/AliDev/ai-projects/

## ⚠️ Hardcoded Paths Found

### In claude-parser:
1. **Test files** (not critical - mock data):
   - `tests/test_phase2/*.py` - Mock JSONL paths
   - `tests/test_phase3/test_watch_api.py` - Sample JSONL path

2. **Scripts** (need updating):
   - `scripts/discover_jsonl_structure.py` - Line 431, 435
   - `scripts/backlog_priorities.py` - Line 14
   - `scripts/discover_structure_simple.py` - Line 180

3. **Documentation** (can update later):
   - `.claude/LOCAL_ENFORCEMENT.md`
   - Various *.md files with examples

### In temporal-hooks:
1. **Documentation only** (not critical):
   - `docs/BACKLOG_COMPLETE.md`
   - `docs/IMPLEMENTATION_GUIDE.md`
   - `docs/IMPLEMENTATION_RULES.md`

## ✅ Safe to Move - No Breaking Changes

The hardcoded paths are mostly in:
- Test files (using mock data)
- Documentation (examples)
- Scripts (can be updated after move)

**No core library code has hardcoded paths!**

## 📋 Migration Steps

### 1. Copy Projects (You do this manually):
```bash
# Create target directory
mkdir -p /Volumes/AliDev/ai-projects/

# Copy claude-parser
cp -r /Users/ali/.claude/projects/claude-parser /Volumes/AliDev/ai-projects/

# Copy temporal-hooks
cp -r /Users/ali/.claude/projects/temporal-hooks /Volumes/AliDev/ai-projects/
```

### 2. Update Git Remotes (Run in new location):
```bash
# For claude-parser
cd /Volumes/AliDev/ai-projects/claude-parser
git remote -v  # Verify it still points to GitHub

# For temporal-hooks (when ready)
cd /Volumes/AliDev/ai-projects/temporal-hooks
git init
git remote add origin https://github.com/alicoding/temporal-hooks.git
```

### 3. Update Environment Variables:
Create `/Volumes/AliDev/ai-projects/.env`:
```bash
# Default paths for the new location
export CLAUDE_PROJECTS_PATH=/Users/ali/.claude/projects/
export SAFE_PROJECT_DIR=/Volumes/AliDev/ai-projects/
export RECOVERY_OUTPUT_DIR=/Volumes/AliDev/ai-projects/recovered/
```

### 4. Test Timeline Still Works:
```python
from claude_parser.timeline import Timeline
from pathlib import Path

# Timeline can still access JSONL from original location
timeline = Timeline(
    Path("/Users/ali/.claude/projects/.../")  # JSONL stays here
)

# But project files are in new location
# This separation is actually GOOD!
```

### 5. Update Scripts (After move):
The scripts that need path updates:
- `scripts/discover_jsonl_structure.py`
- `scripts/backlog_priorities.py`
- `scripts/discover_structure_simple.py`

Can use environment variables instead:
```python
import os
project_dir = os.getenv('SAFE_PROJECT_DIR', '/Volumes/AliDev/ai-projects/')
```

## ✅ Benefits After Migration

1. **Projects safe** from rm -rf in /Volumes/AliDev/
2. **JSONL still accessible** from ~/.claude/projects/
3. **GitHub backup** remains connected
4. **Timeline works** across both locations

## ⚠️ Important Notes

1. **Keep JSONL in original location** - Claude needs to write there
2. **Work in /Volumes/AliDev/** - Your code is safe there
3. **Timeline bridges both** - Can access JSONL and project files

## 🔍 Quick Verification After Move

```bash
# In new location
cd /Volumes/AliDev/ai-projects/claude-parser

# Check git is working
git status
git remote -v

# Test Python import
python -c "from claude_parser import load; print('✅ Import works')"

# Test Timeline with JSONL from old location
python -c "
from claude_parser.timeline import Timeline
from pathlib import Path
t = Timeline(Path('/Users/ali/.claude/projects/'))
print('✅ Timeline works')
"
```

## 🎯 Summary

**It's SAFE to move!** The hardcoded paths are only in test files and docs, not in core functionality. The Timeline design actually benefits from this separation - projects in safe location, JSONL in Claude's location.