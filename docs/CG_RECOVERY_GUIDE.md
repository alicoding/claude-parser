# CG Recovery Guide - Restore Files with 0 Tokens

## Quick Start: Disaster Recovery

### Accidentally deleted a file or folder?

```bash
# Restore a single file
cg checkout path/to/deleted_file.py

# Restore entire folder (coming soon)
cg checkout path/to/deleted_folder/

# See what was deleted
cg status
```

## Common Scenarios

### 1. Deleted a file with `rm`
```bash
rm important_file.py  # Oops!
cg checkout important_file.py  # Restored!
```

### 2. Deleted entire folder with `rm -rf`
```bash
rm -rf src/  # Disaster!

# Option A: Restore each file
cg checkout src/main.py
cg checkout src/utils.py
cg checkout src/config.py

# Option B: Use shell loop (temporary workaround)
for file in $(cg ls-deleted src/); do
  cg checkout "$file"
done
```

### 3. Bad edit from Claude
```bash
# Claude made a bad edit to your file
cg checkout myfile.py  # Restores to version before Claude's last edit
```

### 4. Restore to specific point
```bash
# List recent operations
cg log -n 20

# Restore file to state before specific UUID
cg checkout myfile.py --before <uuid>
```

## How It Works

**Every Claude API call = Automatic Git Commit**

- Every file operation (Write, Edit, MultiEdit) is tracked with a UUID
- Full file content is stored in the JSONL transcript
- `cg checkout` queries the JSONL to find previous versions
- **0 tokens** to restore vs 5000+ tokens for Claude to rewrite

## Installation

```bash
pip install claude-parser

# Or for development
git clone https://github.com/yourusername/claude-parser
cd claude-parser
pip install -e .
```

## Current Limitations

1. **Folder restoration**: Currently requires restoring files one by one
2. **Binary files**: Only text files are stored in JSONL
3. **External changes**: Only tracks changes made through Claude tools

## Roadmap

- [ ] `cg checkout folder/` - Restore entire directories
- [ ] `cg reset --hard <uuid>` - Restore entire project state
- [ ] `cg ls-deleted` - List all deleted files since checkpoint
- [ ] `cg blame <file>` - Show who (human/Claude) made each change

## Technical Details

The JSONL file contains:
```json
{
  "uuid": "unique-id",
  "toolUseResult": "{\"type\":\"create\",\"filePath\":\"/path/to/file\",\"content\":\"full file content\"}",
  "timestamp": "2025-01-14T12:00:00Z"
}
```

DuckDB queries this structure to find previous versions:
```sql
SELECT toolUseResult
FROM 'transcript.jsonl'
WHERE toolUseResult LIKE '%"filePath":"/path/to/file"%'
  AND timestamp < 'checkpoint_time'
ORDER BY timestamp DESC
LIMIT 1
```

## Tips

1. **Always run `cg status` first** to see the current state
2. **Use `cg log` to find UUIDs** for specific restore points
3. **Test with a single file first** before bulk operations
4. **No tokens are used** - this is pure local JSONL querying

## Emergency Contact

If `cg` itself is deleted:
```python
# Emergency restore script
from claude_parser import load_latest_session
from claude_parser.storage.jsonl_engine import get_file_at_checkpoint

session = load_latest_session()
jsonl = session['metadata']['transcript_path']

# Find last checkpoint
checkpoint = "use-uuid-from-terminal-scrollback"
content = get_file_at_checkpoint(jsonl, checkpoint, "path/to/file")
if content:
    with open("path/to/file", "w") as f:
        f.write(content)
```

## Philosophy

> "Every mistake is reversible. Every deletion is temporary. Every bad edit can be undone. Zero tokens required."

This is **Token-Efficient Development** - why spend thousands of tokens having Claude rewrite when you can restore in 0 tokens?