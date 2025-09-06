#!/usr/bin/env python3
"""Check what fields are actually in real Claude data."""

import awkward as ak

def check_real_fields():
    real_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser/0db36546-18ed-482e-8b5d-22b58ef80394.jsonl"

    # Load a few lines to check structure
    with open(real_file, 'r') as f:
        lines = [f.readline().strip() for _ in range(3) if f.readline().strip()]

    events = ak.from_iter([ak.from_json(line) for line in lines])

    print("Real Claude conversation structure:")
    print(f"Fields: {events.fields}")
    print(f"First message: {events[0]}")
    print()

    # Check specific fields we're using
    print("Field availability check:")
    for field in ['type', 'content', 'timestamp', 'uuid', 'session_id', 'name']:
        try:
            value = events[0][field]
            print(f"  {field}: ✅ Available - {value}")
        except Exception:
            print(f"  {field}: ❌ Not available")

if __name__ == "__main__":
    check_real_fields()
