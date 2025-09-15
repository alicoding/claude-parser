# CG Design - Git-Aligned Architecture

## Git Mental Model → CG Implementation

### Git's Three Trees
```
Working Directory  →  Index/Staging  →  Repository (.git)
     (files)           (staged)         (commits)
```

### CG's Two Trees
```
Working Directory  →  JSONL History
     (files)          (every API call)
```

## Command Mapping

### Single File Restoration
```bash
# Git
git checkout -- file.txt           # From index
git checkout HEAD -- file.txt      # From last commit

# CG
cg checkout file.txt               # From last checkpoint
cg checkout file.txt --uuid ABC    # From specific point
```

### Folder Restoration (rm -rf recovery)
```bash
# Git - restores entire folder
git checkout -- src/

# CG - should restore entire folder
cg checkout src/
```

## Implementation Plan

### Phase 1: Status Command Enhancement
```python
def status():
    """Compare filesystem vs JSONL history"""
    # 1. Get all files from last checkpoint in JSONL
    jsonl_files = query_jsonl("SELECT DISTINCT filePath...")

    # 2. Get all files from filesystem
    disk_files = Path('.').glob('**/*')

    # 3. Show deleted (in JSONL but not on disk)
    deleted = jsonl_files - disk_files

    # 4. Show untracked (on disk but not in JSONL)
    untracked = disk_files - jsonl_files
```

### Phase 2: Folder Checkout
```python
def checkout(target: str):
    if target.endswith('/'):
        # Folder checkout - restore all with prefix
        files = query_jsonl(f"""
            SELECT DISTINCT
                toolUseResult->>'$.filePath' as path,
                toolUseResult->>'$.content' as content
            FROM jsonl
            WHERE toolUseResult->>'$.filePath' LIKE '{target}%'
              AND timestamp < checkpoint
        """)

        for file_path, content in files:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).write_text(content)
    else:
        # Single file (existing logic)
```

### Phase 3: List Deleted Files
```python
@app.command()
def ls_files(deleted: bool = typer.Option(False, "--deleted")):
    """List files like git ls-files"""
    if deleted:
        # Files in JSONL but not on disk
        jsonl_files = get_all_files_from_jsonl()
        disk_files = set(Path('.').glob('**/*'))

        for file in jsonl_files - disk_files:
            console.print(file, style="red")
```

### Phase 4: Restore Everything
```python
@app.command()
def checkout(target: str = typer.Argument(".")):
    """Restore files - supports . for everything"""
    if target == ".":
        # Restore entire working directory
        restore_all_from_checkpoint()
```

## SQL Queries Needed

### 1. Get all files at checkpoint
```sql
WITH last_checkpoint AS (
    SELECT uuid, timestamp
    FROM jsonl
    WHERE toolUseResult LIKE '%filePath%'
    ORDER BY timestamp DESC
    LIMIT 1
)
SELECT DISTINCT
    toolUseResult->>'$.filePath' as file_path,
    FIRST_VALUE(toolUseResult->>'$.content')
        OVER (PARTITION BY toolUseResult->>'$.filePath'
              ORDER BY timestamp DESC) as content
FROM jsonl
WHERE timestamp <= (SELECT timestamp FROM last_checkpoint)
  AND toolUseResult IS NOT NULL
  AND toolUseResult LIKE '%filePath%'
```

### 2. Get files with prefix (folder)
```sql
SELECT toolUseResult
FROM jsonl
WHERE toolUseResult LIKE '%"filePath":"src/%'
  AND timestamp < checkpoint_time
ORDER BY timestamp DESC
```

### 3. Get deleted files
```sql
-- All unique files ever created
SELECT DISTINCT toolUseResult->>'$.filePath' as path
FROM jsonl
WHERE toolUseResult->>'$.type' IN ('create', 'write')

-- Then compare with filesystem in Python
```

## Edge Cases

### 1. Binary Files
- Git tracks binary files in objects
- CG only has text in JSONL
- Solution: Show warning for binary files

### 2. Symbolic Links
- Git preserves symlinks
- CG treats as regular files
- Solution: Document limitation

### 3. File Permissions
- Git tracks executable bit
- CG doesn't track permissions
- Solution: Restore with default permissions

### 4. Empty Directories
- Git doesn't track empty dirs
- CG doesn't either
- Solution: Same as git - ignore

## Testing Plan

```bash
# Test setup
mkdir test_project
cd test_project
echo "file1" > src/file1.txt
echo "file2" > src/file2.txt
echo "file3" > src/utils/file3.txt

# Disaster scenario
rm -rf src/

# Recovery test
cg status                    # Should show 3 deleted files
cg ls-files --deleted       # Should list all 3
cg checkout src/            # Should restore entire folder
ls -la src/                 # Should have all files back
```

## Benefits of Git Alignment

1. **Familiar UX**: Users who know git instantly understand cg
2. **Proven patterns**: Git's model has 20+ years of refinement
3. **Clear mental model**: Working directory vs history
4. **Predictable behavior**: Acts like git minus staging area

## Key Differences from Git

| Feature | Git | CG |
|---------|-----|-----|
| Staging area | Yes (index) | No |
| Commits | Manual | Every API call |
| Binary files | Full support | Text only |
| History rewriting | Yes (rebase) | No (immutable) |
| Branches | Yes | No (linear) |
| Merge conflicts | Yes | No (last write wins) |

## Implementation Priority

1. ✅ Single file checkout (DONE)
2. ⏳ Folder checkout for `rm -rf` recovery
3. ⏳ Enhanced status showing deletions
4. ⏳ ls-files --deleted command
5. ⏳ Checkout . (restore everything)
6. ⏳ Diff against checkpoint
7. ⏳ Log with file changes

This design ensures `cg` feels natural to git users while leveraging the unique aspects of Claude's JSONL-based history.