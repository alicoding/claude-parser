#!/usr/bin/env python3
"""Debug parsing errors in JSONL file."""

from pathlib import Path
from claude_parser import load
from claude_parser.infrastructure.message_repository import JsonlMessageRepository
import orjson

jsonl_file = Path("~/.claude/projects/-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2/8f64b245-7268-4ecd-9b90-34037f3c5b75.jsonl")

# Load with repository to see errors
repo = JsonlMessageRepository()
messages = repo.load_messages(jsonl_file)

print(f"Loaded {len(messages)} messages")
print(f"Errors: {len(repo._errors)}")

# Show first few errors
for line_num, error in repo._errors[:5]:
    print(f"Line {line_num}: {error}")

# Read actual lines to see what's failing
with open(jsonl_file, 'rb') as f:
    lines = f.readlines()
    
# Check specific error lines
if repo._errors:
    first_error_line = repo._errors[0][0] - 1  # Convert to 0-based
    if first_error_line < len(lines):
        print(f"\nFirst error line content:")
        raw_msg = orjson.loads(lines[first_error_line])
        print(f"Type: {raw_msg.get('type')}")
        if 'message' in raw_msg:
            print(f"Has message field")
        print(f"Keys: {list(raw_msg.keys())[:10]}")