#!/usr/bin/env python3
"""Debug the actual array structure more carefully."""

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
    print(f"Fields: {events.fields}")
    print()

    print("Event details:")
    for i in range(len(events)):
        print(f"events[{i}]: {events[i]}")
        print(f"  Full event: {dict(events[i])}")
        print(f"  Type field: {events[i]['type']}")
        print()

    print("Field access tests:")
    type_field = events["type"]
    print(f"events['type'] = {type_field}")
    print(f"Type of type_field: {type(type_field)}")

    print("Comparison test:")
    user_mask = events["type"] == "user"
    print(f"user_mask = {user_mask}")
    print(f"Type of user_mask: {type(user_mask)}")

if __name__ == "__main__":
    debug_events()
