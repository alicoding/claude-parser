#!/usr/bin/env python3
"""
Task validation for dstask - enforces 95/5 and DRY principles.

This script can be used as:
1. Pre-commit hook in ~/.dstask/.git/hooks/
2. Manual validation: python validate_task.py <task_id>
3. Automated enrichment on task creation
"""

import subprocess
import orjson
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import re


def get_task_notes(task_id: int) -> str:
    """Get notes for a specific task."""
    result = subprocess.run(
        ["dstask", str(task_id), "note"],
        capture_output=True,
        text=True
    )
    return result.stdout


def validate_task_notes(notes: str) -> Tuple[bool, List[str]]:
    """Validate task notes have required information."""
    issues = []

    # Check for required sections
    required_sections = [
        ("LIBRARIES:", "No library research documented"),
        ("COMPLEXITY:", "No complexity target set"),
        ("DUPLICATES:", "No duplicate check documented"),
        ("SUCCESS:", "No success criteria defined"),
    ]

    for section, error_msg in required_sections:
        if section not in notes.upper():
            issues.append(error_msg)

    # Check for forbidden patterns
    if "for .* in" in notes.lower() and "toolz" not in notes.lower():
        issues.append("Manual loops mentioned without toolz alternative")

    # Check for line limit
    if "150" not in notes and "LOC" not in notes.upper():
        issues.append("No line limit consideration")

    return len(issues) == 0, issues


def suggest_libraries(task_summary: str) -> List[str]:
    """Suggest libraries based on task summary."""
    suggestions = []

    keywords = {
        "parse": ["orjson", "pydantic"],
        "analyze": ["toolz", "pandas"],
        "iterate": ["toolz", "more-itertools"],
        "filter": ["toolz.filter", "funcy"],
        "map": ["toolz.map", "funcy.map"],
        "time": ["pendulum"],
        "http": ["httpx"],
        "cli": ["typer"],
    }

    for keyword, libs in keywords.items():
        if keyword in task_summary.lower():
            suggestions.extend(libs)

    return list(set(suggestions))


def check_for_duplicates(task_summary: str) -> List[str]:
    """Check for potential duplicate implementations."""
    # This would grep the codebase for similar functionality
    duplicates = []

    # Check for common duplicate patterns
    if "stats" in task_summary.lower() or "statistics" in task_summary.lower():
        duplicates.append("Found existing: ConversationStats, SessionStats, TokenStats")

    if "analyze" in task_summary.lower():
        duplicates.append("Found existing: analyzer.py, session_analyzer.py, token_analyzer.py")

    return duplicates


def main():
    """Validate task or enrich with suggestions."""
    if len(sys.argv) < 2:
        print("Usage: python validate_task.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]

    # Get task details
    notes = get_task_notes(task_id)

    # Validate
    valid, issues = validate_task_notes(notes)

    if not valid:
        print(f"❌ Task {task_id} validation failed:")
        for issue in issues:
            print(f"  - {issue}")

        # Suggest fixes
        print("\n💡 Suggestions:")
        print("  1. Run: python scripts/research.py '<task description>'")
        print("  2. Check for duplicates: grep -r 'similar_function' claude_parser/")
        print("  3. Set complexity target: radon cc <file> should be A or B")
        print("  4. Add SUCCESS criteria for testing")

        sys.exit(1)
    else:
        print(f"✅ Task {task_id} is properly documented!")
        sys.exit(0)


if __name__ == "__main__":
    main()
