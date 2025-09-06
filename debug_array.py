#!/usr/bin/env python3
"""Debug the actual array structure."""

import awkward as ak

def debug_events():
    file_path = "/Volumes/AliDev/ai-projects/claude-parser/test_sample.jsonl"

    # Load the data
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    events = ak.from_iter([ak.from_json(line) for line in lines])

    print("Array structure:")
    print(f"Type: {type(events)}")
    print(f"Length: {len(events)}")
    print(f"Schema: {events.type}")
    print()

    print("Event types:")
    for i in range(len(events)):
        print(f"events[{i}].type = {events[i].type} (type: {type(events[i].type)})")
    print()

    print("Comparison results:")
    user_mask = events.type == "user"
    print(f"user_mask = {user_mask} (type: {type(user_mask)})")
    print(f"ak.is_scalar(user_mask) = {ak.is_scalar(user_mask)}")

    # Try to sum manually
    count = 0
    for i in range(len(events)):
        if events[i].type == "user":
            count += 1
    print(f"Manual count of 'user': {count}")

if __name__ == "__main__":
    debug_events()
