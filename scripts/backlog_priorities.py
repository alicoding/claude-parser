#!/usr/bin/env python3
"""Extract and display backlog priorities with notes from tags."""

import subprocess
import orjson
from typing import List, Dict, Any

def get_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from dstask."""
    result = subprocess.run(
        ["dstask", "show-open"],
        capture_output=True,
        text=True,
        cwd="/Users/ali/.claude/projects/claude-parser"
    )
    return orjson.loads(result.stdout)

def extract_notes(tags: List[str]) -> str:
    """Extract notes from tags that start with 'notes:'."""
    from toolz import pipe, filter, map
    from operator import methodcaller
    
    notes = pipe(
        tags,
        lambda t: filter(methodcaller('startswith', 'notes:'), t),
        lambda t: map(lambda tag: tag[6:], t),  # Remove 'notes:' prefix
        list
    )
    return "\n\n".join(notes) if notes else ""

def print_task_priorities():
    """Display tasks organized by priority with extracted notes."""
    tasks = get_tasks()
    
    # Group by priority
    from toolz import groupby
    from operator import methodcaller
    
    # Add extracted notes to each task
    tasks_with_notes = [
        {**task, "extracted_notes": extract_notes(task.get("tags", []))}
        for task in tasks
    ]
    
    # Group by priority
    by_priority = groupby(methodcaller('get', 'priority', 'P2'), tasks_with_notes)
    by_priority = {k: list(v) for k, v in by_priority.items()}
    
    # Ensure all priority levels exist
    for p in ["P0", "P1", "P2", "P3"]:
        if p not in by_priority:
            by_priority[p] = []
    
    # Display P0 tasks (Critical)
    print("=" * 80)
    print("🔴 P0 - CRITICAL PRIORITY (Do First)")
    print("=" * 80)
    
    for task in by_priority["P0"]:
        print(f"\nTask {task['id']}: {task['summary']}")
        print(f"Project: {task.get('project', 'none')}")
        if task["extracted_notes"]:
            print("\n📝 Notes:")
            # Show first 200 chars of notes
            notes_preview = task["extracted_notes"][:200]
            if len(task["extracted_notes"]) > 200:
                notes_preview += "..."
            print(notes_preview)
        print("-" * 40)
    
    # Show counts for other priorities
    print("\n📊 Summary:")
    print(f"P0 (Critical): {len(by_priority['P0'])} tasks")
    print(f"P1 (High): {len(by_priority['P1'])} tasks")
    print(f"P2 (Normal): {len(by_priority['P2'])} tasks")
    
    # Identify ready tasks with STATUS: READY
    ready_tasks = []
    for priority in ["P0", "P1", "P2"]:
        for task in by_priority[priority]:
            if "STATUS: READY" in task["extracted_notes"]:
                ready_tasks.append((task["id"], task["summary"]))
    
    if ready_tasks:
        print("\n✅ READY TO IMPLEMENT (Have complete context):")
        for task_id, summary in ready_tasks[:5]:
            print(f"  Task {task_id}: {summary}")

if __name__ == "__main__":
    print_task_priorities()