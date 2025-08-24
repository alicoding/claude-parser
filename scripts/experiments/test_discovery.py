#!/usr/bin/env python
"""Test discovery tool with real data."""

from pathlib import Path
from claude_parser.discovery import find_transcript_for_cwd, list_all_projects

# Test with real project paths (from actual cwd values)
test_paths = [
    Path("/Volumes/AliDev/ai-projects/claude-intelligence-center"),
    Path("/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2"),  # Correct path with /
    Path("/Volumes/AliDev/ai-projects/memory"),
    Path("/Volumes/AliDev/ai-projects/draw-my-idea"),
]

print("Testing discovery tool with real project paths...")
print("=" * 60)

for project_path in test_paths:
    print(f"\nProject: {project_path}")
    transcript = find_transcript_for_cwd(project_path)
    if transcript:
        print(f"  ✅ Found transcript: {Path(transcript).name}")
    else:
        print(f"  ❌ No transcript found")

print("\n" + "=" * 60)
print("\nListing all Claude projects:")
projects = list_all_projects()
print(f"Found {len(projects)} projects total")

# Show first 5 projects
for project in projects[:5]:
    print(f"\n  {project['decoded_path']}")
    print(f"    Transcripts: {project['transcript_count']}")
    if project['most_recent']:
        print(f"    Most recent: {project['most_recent'].name}")