#!/usr/bin/env python3
"""
Audit all tasks for proper context and flag for refinement.

This script:
1. Checks all open tasks for required context
2. Flags tasks missing critical information
3. Suggests refinements
4. Can bulk-update tasks with template
"""

import subprocess
import orjson
import sys
from typing import Dict, List, Tuple
from pathlib import Path


REQUIRED_SECTIONS = [
    "PRINCIPLES",
    "RESEARCH", 
    "DUPLICATES",
    "COMPLEXITY",
    "SUCCESS CRITERIA",
    "VALIDATION"
]

TEMPLATE = """NEEDS REFINEMENT - ADD CONTEXT
=====================================

ORIGINAL: {summary}

PRINCIPLES (REQUIRED):
- 95/5: Use libraries for 95% of code
- DRY: No duplication allowed
- SOLID: Single responsibility
- LOC: Max 150 lines per file

RESEARCH (REQUIRED):
- [ ] Run: python scripts/research.py "{summary}"
- Libraries found: [TO BE FILLED]
- Recommended approach: [TO BE FILLED]

DUPLICATES (REQUIRED):
- [ ] Check with: grep -r 'related_terms' claude_parser/
- Similar implementations: [TO BE FILLED]
- Reusable components: [TO BE FILLED]

COMPLEXITY (REQUIRED):
- Target: A or B only
- Current files affected: [TO BE FILLED]
- Refactoring needed: [TO BE FILLED]

SUCCESS CRITERIA (REQUIRED):
□ verify_spec.py passes
□ No files over 150 LOC
□ No manual loops
□ Tests pass

VALIDATION (REQUIRED):
- Before: [commands to run]
- After: python scripts/verify_spec.py

STATUS: NEEDS CONTEXT - Cannot start until refined
"""


def get_all_tasks() -> List[Dict]:
    """Get all open tasks from dstask."""
    result = subprocess.run(
        ["dstask", "show-open", "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return orjson.loads(result.stdout)
    return []


def check_task_context(task: Dict) -> Tuple[bool, List[str]]:
    """Check if task has proper context."""
    notes = task.get("notes", "")
    issues = []
    
    # Check minimum length
    if len(notes) < 500:
        issues.append("Notes too short (min 500 chars)")
    
    # Check for required sections
    for section in REQUIRED_SECTIONS:
        if section not in notes.upper():
            issues.append(f"Missing {section} section")
    
    # Check for research
    if "python scripts/research.py" not in notes:
        issues.append("No research command documented")
    
    # Check for validation
    if "verify_spec.py" not in notes:
        issues.append("No validation criteria")
    
    return len(issues) == 0, issues


def flag_task(task_id: int, issues: List[str]) -> None:
    """Flag a task as needing refinement."""
    # Add a tag
    subprocess.run(
        ["dstask", str(task_id), "modify", "+needs-context"],
        capture_output=True
    )
    
    # Update priority if not already high
    subprocess.run(
        ["dstask", str(task_id), "modify", "P2"],
        capture_output=True
    )


def generate_refinement(task: Dict) -> str:
    """Generate refinement template for task."""
    return TEMPLATE.format(summary=task.get("summary", ""))


def audit_all_tasks(fix: bool = False) -> None:
    """Audit all tasks and optionally fix them."""
    tasks = get_all_tasks()
    print(f"🔍 Auditing {len(tasks)} open tasks...\n")
    
    needs_refinement = []
    has_context = []
    
    for task in tasks:
        task_id = task["id"]
        summary = task["summary"][:60]
        
        valid, issues = check_task_context(task)
        
        if not valid:
            needs_refinement.append((task_id, summary, issues))
            if fix:
                flag_task(task_id, issues)
        else:
            has_context.append((task_id, summary))
    
    # Report results
    print(f"📊 AUDIT RESULTS:")
    print(f"✅ Tasks with proper context: {len(has_context)}")
    print(f"❌ Tasks needing refinement: {len(needs_refinement)}")
    
    if needs_refinement:
        print(f"\n🚨 TASKS NEEDING CONTEXT:")
        for task_id, summary, issues in needs_refinement[:10]:
            print(f"\nTask {task_id}: {summary}")
            for issue in issues:
                print(f"  - {issue}")
        
        if len(needs_refinement) > 10:
            print(f"\n... and {len(needs_refinement) - 10} more")
    
    # Suggest bulk operations
    if needs_refinement and not fix:
        print(f"\n💡 TO FIX ALL:")
        print(f"python scripts/audit_tasks.py --fix")
        print(f"This will tag all {len(needs_refinement)} tasks with 'needs-context'")
    
    # Create refinement script
    if needs_refinement:
        print(f"\n📝 GENERATING REFINEMENT TEMPLATES...")
        with open("/tmp/task_refinements.txt", "w") as f:
            for task_id, summary, issues in needs_refinement:
                f.write(f"\n{'='*60}\n")
                f.write(f"TASK {task_id}: {summary}\n")
                f.write(f"ISSUES: {', '.join(issues)}\n")
                f.write(f"{'='*60}\n")
                f.write(generate_refinement({"summary": summary}))
        
        print(f"Templates saved to: /tmp/task_refinements.txt")
        print(f"Apply with: dstask <id> note < /tmp/task_refinements.txt")


def create_phase_tasks() -> None:
    """Create properly contexted tasks for each cleanup phase."""
    phases = [
        "Phase 1: Consolidate 3 Stats classes into UnifiedStats",
        "Phase 2: Create shared extractors using toolz",
        "Phase 3: Merge 3 analyzer services into UnifiedAnalyzer",
        "Phase 4: Split 6 files over 150 LOC",
        "Phase 5: Replace all loops with toolz functions",
        "Phase 6: Activate enforcement and achieve 100% green"
    ]
    
    print("📝 Creating phase tasks with full context...")
    
    for phase in phases:
        cmd = ["./scripts/ctask", "add", phase]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "Created task" in result.stdout:
            print(f"✅ {phase}")
        else:
            print(f"❌ Failed: {phase}")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--fix":
            audit_all_tasks(fix=True)
        elif sys.argv[1] == "--create-phases":
            create_phase_tasks()
        else:
            print("Usage: python audit_tasks.py [--fix|--create-phases]")
    else:
        audit_all_tasks(fix=False)


if __name__ == "__main__":
    main()