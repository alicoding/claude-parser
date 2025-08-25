#!/usr/bin/env python3
"""
Enforced task creation for Claude Code sessions.

This ensures EVERY task has FULL CONTEXT before any Claude agent works on it.
No more partial implementations, no more violations, no more tech debt.

Usage:
    python create_enforced_task.py "Task description"
    
This will:
1. Research libraries automatically
2. Check for duplicates
3. Analyze affected files
4. Create task with COMPLETE context
"""

import subprocess
import sys
from pathlib import Path
import orjson
from typing import List, Dict, Tuple
import re
from datetime import datetime


def run_research(query: str) -> str:
    """Run research.py to find libraries."""
    result = subprocess.run(
        ["python", "scripts/research.py", query],
        capture_output=True,
        text=True,
        cwd="/Volumes/AliDev/ai-projects/claude-parser"
    )
    # Extract the key recommendations
    if "Research Results:" in result.stdout:
        return result.stdout.split("Research Results:")[1].split("📁")[0].strip()
    return "No research results found"


def check_for_duplicates(keywords: List[str]) -> List[str]:
    """Check codebase for potential duplicates."""
    duplicates = []
    
    for keyword in keywords:
        # Check for existing implementations
        result = subprocess.run(
            ["grep", "-r", f"def.*{keyword}", "claude_parser", "--include=*.py"],
            capture_output=True,
            text=True
        )
        if result.stdout:
            files = set(line.split(":")[0] for line in result.stdout.strip().split("\n"))
            duplicates.extend(files)
    
    return list(set(duplicates))


def analyze_complexity(files: List[str]) -> Dict[str, str]:
    """Run radon complexity check on files."""
    complexity = {}
    
    for file in files:
        if Path(file).exists():
            result = subprocess.run(
                ["radon", "cc", file, "-s", "-n", "B"],
                capture_output=True,
                text=True
            )
            if "B (" in result.stdout or "C (" in result.stdout:
                complexity[file] = "HIGH - needs refactoring"
            else:
                complexity[file] = "OK"
    
    return complexity


def get_file_sizes(pattern: str) -> List[Tuple[str, int]]:
    """Get files matching pattern with line counts."""
    result = subprocess.run(
        ["find", "claude_parser", "-name", "*.py", "-type", "f", "-exec", "wc", "-l", "{}", ";"],
        capture_output=True,
        text=True
    )
    
    oversized = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.strip().split()
            if len(parts) >= 2:
                lines = int(parts[0])
                filepath = parts[1]
                if lines > 150 and pattern.lower() in filepath.lower():
                    oversized.append((filepath, lines))
    
    return oversized


def extract_keywords(description: str) -> List[str]:
    """Extract keywords from task description."""
    # Remove common words
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "as", "is", "was", "are", "were"}
    
    # Extract meaningful words
    words = re.findall(r'\b[a-z]+\b', description.lower())
    keywords = [w for w in words if w not in stopwords and len(w) > 3]
    
    return keywords


def create_task_with_context(description: str) -> None:
    """Create a task with FULL ENFORCED CONTEXT."""
    
    print(f"🔍 Analyzing: {description}")
    
    # Extract keywords
    keywords = extract_keywords(description)
    print(f"📌 Keywords: {', '.join(keywords)}")
    
    # 1. Research libraries
    print("📚 Researching libraries...")
    research = run_research(description)
    
    # 2. Check for duplicates
    print("🔎 Checking for duplicates...")
    duplicates = check_for_duplicates(keywords)
    
    # 3. Analyze complexity of related files
    print("📊 Analyzing complexity...")
    complexity = analyze_complexity(duplicates) if duplicates else {}
    
    # 4. Check file sizes
    print("📏 Checking file sizes...")
    oversized = []
    for keyword in keywords[:3]:  # Check top 3 keywords
        oversized.extend(get_file_sizes(keyword))
    
    # 5. Build the ENFORCED task note
    note = f"""ENFORCED CONTEXT - GENERATED {datetime.now().isoformat()}
==================================================

TASK: {description}

PRINCIPLES (MANDATORY):
- 95/5: Use libraries for 95% of code
- DRY: No duplication allowed
- SOLID: Single responsibility per file
- DDD: Domain boundaries respected
- LOC: Max 150 lines per file

RESEARCH COMPLETED:
{research[:500]}

LIBRARIES TO USE:
- orjson (NOT json)
- pendulum (NOT datetime)
- toolz/funcy (NOT manual loops)
- httpx (NOT requests)
- typer (NOT argparse)

DUPLICATE CHECK:
{f"Found {len(duplicates)} potential duplicates:" if duplicates else "No duplicates found"}
{chr(10).join(f"- {d}" for d in duplicates[:10])}

COMPLEXITY ANALYSIS:
{chr(10).join(f"- {f}: {c}" for f, c in list(complexity.items())[:5])}

FILES OVER 150 LOC:
{chr(10).join(f"- {f}: {l} lines" for f, l in oversized[:5])}

IMPLEMENTATION STRATEGY:
1. Check existing code in: {', '.join(duplicates[:3]) if duplicates else 'No existing code'}
2. Reuse existing patterns/services
3. Use toolz for all iterations
4. Split any file approaching 150 LOC
5. Run radon cc before committing

SUCCESS CRITERIA:
✓ No new files over 150 LOC
✓ Radon complexity A or B only
✓ All loops use toolz/funcy
✓ No duplicate implementations
✓ Tests pass
✓ verify_spec.py passes

VALIDATION COMMANDS:
- python scripts/verify_spec.py
- radon cc <file> -n B
- pytest tests/
- grep -c "for .* in" <file>  # Should be 0

STATUS: READY FOR IMPLEMENTATION
"""
    
    # 6. Create the task with full context
    cmd = ["dstask", "add", description, "-p", "claude-parser"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if "Added" in result.stdout:
        # Extract task ID
        task_id = result.stdout.split("Added ")[1].split(":")[0]
        
        # Add the comprehensive note
        subprocess.run(["dstask", task_id, "note", note])
        
        print(f"✅ Created task {task_id} with ENFORCED CONTEXT")
        print(f"📝 Task has {len(note)} chars of context")
        print(f"🚀 Task is READY for any Claude agent to implement")
        
        # Show the task
        subprocess.run(["dstask", task_id, "info"])
    else:
        print(f"❌ Failed to create task: {result.stderr}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_enforced_task.py 'Task description'")
        print("\nThis will create a task with FULL CONTEXT including:")
        print("- Library research")
        print("- Duplicate detection")
        print("- Complexity analysis")
        print("- File size checks")
        print("- Implementation strategy")
        print("- Success criteria")
        sys.exit(1)
    
    description = " ".join(sys.argv[1:])
    create_task_with_context(description)


if __name__ == "__main__":
    main()