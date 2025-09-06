#!/usr/bin/env python3
"""Debug Awkward Array JSON loading."""

import awkward as ak
from pathlib import Path

def test_awkward_loading():
    file_path = "/Volumes/AliDev/ai-projects/claude-parser/test_sample.jsonl"

    print(f"Testing file path: {file_path}")
    print(f"File exists: {Path(file_path).exists()}")
    print(f"File size: {Path(file_path).stat().st_size if Path(file_path).exists() else 'N/A'}")

    try:
        # Test with line_delimited=True for JSONL
        print("\n1. Testing ak.from_json with line_delimited=True:")
        events = ak.from_json(file_path, line_delimited=True)
        print(f"Success! Loaded {len(events)} events")
        print(f"First event type: {events.type[0] if len(events) > 0 else 'None'}")

    except Exception as e:
        print(f"Error with line_delimited=True: {e}")

    try:
        # Test reading file manually first
        print("\n2. Testing manual file read + ak.from_json:")
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"File content length: {len(content)}")
            print("First 100 chars:", content[:100])

        # Try parsing each line individually
        lines = content.strip().split('\n')
        print(f"Number of lines: {len(lines)}")

        # Parse line by line
        events = ak.from_iter([ak.from_json(line) for line in lines])
        print(f"Success with line-by-line parsing! Loaded {len(events)} events")

    except Exception as e:
        print(f"Error with manual approach: {e}")

if __name__ == "__main__":
    test_awkward_loading()
