#!/usr/bin/env python3
"""
Backlog management script for claude-parser using dstask.
This script can be run by Claude Code to manage tasks autonomously.

95/5 Principle: Uses dstask CLI for task management
LIBRARY FIRST: Uses subprocess for CLI interaction, orjson for JSON
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Optional
import orjson
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

class DstaskManager:
    """Manages backlog using dstask CLI."""
    
    def __init__(self, project: str = "claude-parser"):
        self.project = project
        
    def add_task(self, summary: str, priority: str = "P2", tags: List[str] = None, notes: str = None) -> str:
        """Add a new task to backlog."""
        cmd = ["dstask", "add", summary, f"project:{self.project}"]
        
        # Add priority
        if priority in ["P0", "P1", "P2", "P3"]:
            cmd.append(priority)
            
        # Add tags
        if tags:
            for tag in tags:
                cmd.append(f"+{tag}")
                
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Extract task ID from output
        if "Added" in result.stdout:
            task_id = result.stdout.split("Added ")[1].split(":")[0]
            
            # Add notes if provided
            if notes:
                self.add_note(task_id, notes)
                
            return task_id
        return ""
    
    def add_note(self, task_id: str, note: str):
        """Add note to existing task."""
        # Write note to temp file for multi-line support
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(note)
            temp_path = f.name
            
        # Use editor mode to add note
        subprocess.run(["dstask", task_id, "note"], 
                      env={**subprocess.os.environ, "EDITOR": f"cat {temp_path} >>"})
        Path(temp_path).unlink()
    
    def list_tasks(self, filter_str: str = "") -> List[Dict]:
        """List tasks with optional filter."""
        cmd = ["dstask", "show-open"]
        if filter_str:
            cmd.append(filter_str)
            
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Parse dstask output (would need more sophisticated parsing)
        return []
    
    def complete_task(self, task_id: str):
        """Mark task as done."""
        subprocess.run(["dstask", task_id, "done"])
    
    def start_task(self, task_id: str):
        """Start working on task."""
        subprocess.run(["dstask", task_id, "start"])
    
    def get_next_tasks(self) -> str:
        """Get prioritized next tasks."""
        result = subprocess.run(["dstask", "next"], capture_output=True, text=True)
        return result.stdout


def init_backlog():
    """Initialize backlog with current tasks from documentation."""
    manager = DstaskManager()
    
    # Core issues to fix (P0 - Critical)
    critical_tasks = [
        {
            "summary": "Fix 5 files exceeding 150 LOC limit",
            "priority": "P0",
            "tags": ["refactor", "95-5-violation"],
            "notes": """Files to split:
- transcript_finder.py: 265 lines → Split into finder + mapper
- watcher.py: 158 lines → Extract IncrementalReader
- conversation_service.py: 183 lines → Split service methods
- jsonl_parser.py: 242 lines → Split validation logic
- message_repository.py: 199 lines → Extract metadata logic
"""
        },
        {
            "summary": "Complete hook system PostToolUse verification",
            "priority": "P0", 
            "tags": ["hooks", "testing"],
            "notes": "PostToolUse hook is working but needs more comprehensive testing"
        }
    ]
    
    # High priority improvements (P1)
    high_priority = [
        {
            "summary": "Implement WatcherManager for non-blocking file monitoring",
            "priority": "P1",
            "tags": ["watch", "feature"],
            "notes": """Needed by memory project:
- Non-blocking watch with status checking
- Backend auto-detection (Celery/RQ/in-memory)
- manager.get_status() for active watchers
"""
        },
        {
            "summary": "Add streaming support for large JSONL files",
            "priority": "P1",
            "tags": ["performance", "parser"],
            "notes": "Use generators and lazy evaluation for files > 100MB"
        },
        {
            "summary": "Create AI context auto-update hook",
            "priority": "P1",
            "tags": ["hooks", "ai-context"],
            "notes": "SessionStart hook that loads CODEBASE_INVENTORY.json"
        }
    ]
    
    # Normal priority features (P2)
    normal_priority = [
        {
            "summary": "Add export functionality for conversations",
            "priority": "P2",
            "tags": ["export", "feature"],
            "notes": "Export to Markdown, JSON, or HTML formats"
        },
        {
            "summary": "Implement conversation diffing",
            "priority": "P2",
            "tags": ["analysis", "feature"],
            "notes": "Compare two conversation states, show what changed"
        },
        {
            "summary": "Add token counting and cost estimation",
            "priority": "P2",
            "tags": ["analytics", "feature"],
            "notes": "Track input/output/cache tokens with cost calculation"
        },
        {
            "summary": "Build TypeScript SDK",
            "priority": "P2",
            "tags": ["typescript", "sdk"],
            "notes": "Mirror Python API in TypeScript using Zod for validation"
        }
    ]
    
    # Low priority/nice-to-have (P3)
    low_priority = [
        {
            "summary": "Add conversation visualization",
            "priority": "P3",
            "tags": ["visualization", "feature"],
            "notes": "Generate mermaid diagrams or D3 visualizations"
        },
        {
            "summary": "Create conversation templates",
            "priority": "P3",
            "tags": ["templates", "feature"],
            "notes": "Pre-built conversation patterns for common use cases"
        }
    ]
    
    # Add all tasks
    console.print("[bold green]Initializing claude-parser backlog in dstask...[/bold green]")
    
    for task_group in [critical_tasks, high_priority, normal_priority, low_priority]:
        for task in task_group:
            task_id = manager.add_task(
                task["summary"],
                task["priority"],
                task.get("tags", []),
                task.get("notes", "")
            )
            if task_id:
                console.print(f"✓ Added task {task_id}: {task['summary'][:50]}...")
    
    # Show summary
    console.print("\n[bold yellow]Backlog initialized! Next steps:[/bold yellow]")
    result = manager.get_next_tasks()
    console.print(result)


def show_status():
    """Show current backlog status."""
    manager = DstaskManager()
    
    # Create status table
    table = Table(title="Claude Parser Backlog Status", box=box.ROUNDED)
    table.add_column("Priority", style="cyan")
    table.add_column("Count", style="magenta")
    
    # Get counts by priority (would need proper parsing)
    console.print(table)
    
    # Show next tasks
    console.print("\n[bold]Next Tasks:[/bold]")
    console.print(manager.get_next_tasks())


def main():
    """Main CLI interface."""
    import sys
    
    if len(sys.argv) < 2:
        console.print("Usage: manage_backlog.py [init|status|add|done|next]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_backlog()
    elif command == "status":
        show_status()
    elif command == "next":
        manager = DstaskManager()
        console.print(manager.get_next_tasks())
    elif command == "add" and len(sys.argv) > 2:
        manager = DstaskManager()
        summary = " ".join(sys.argv[2:])
        task_id = manager.add_task(summary)
        console.print(f"Added task {task_id}")
    elif command == "done" and len(sys.argv) > 2:
        manager = DstaskManager()
        manager.complete_task(sys.argv[2])
        console.print(f"Completed task {sys.argv[2]}")
    else:
        console.print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()