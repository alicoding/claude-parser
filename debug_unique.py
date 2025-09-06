#!/usr/bin/env python3
"""Check Awkward Array unique function."""

import awkward as ak

# Check available functions
print("Available ak functions with 'unique':")
for name in dir(ak):
    if 'unique' in name.lower():
        print(f"  {name}")

# Test with data
file_path = "/Volumes/AliDev/ai-projects/claude-parser/test_sample.jsonl"
with open(file_path, 'r') as f:
    lines = [line.strip() for line in f if line.strip()]
events = ak.from_iter([ak.from_json(line) for line in lines])

print(f"\nSession IDs: {events['session_id']}")

# Try to get unique values manually
session_ids = [str(events[i]["session_id"]) for i in range(len(events))]
unique_sessions = list(set(session_ids))
print(f"Unique sessions (manual): {unique_sessions}")
print(f"Count: {len(unique_sessions)}")
