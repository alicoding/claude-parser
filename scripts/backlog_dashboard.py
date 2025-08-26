#!/usr/bin/env python3
"""
Backlog dashboard for Claude Code to autonomously manage tasks.
This provides a clean interface that Claude Code can use to track progress.

95/5: Uses dstask for task management, rich for display
"""

import subprocess
import orjson
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich import box
from typing import List, Dict
import sys

console = Console()

def parse_dstask_json(json_output: str) -> List[Dict]:
    """Parse dstask JSON output."""
    try:
        return orjson.loads(json_output)
    except:
        return []

def get_tasks_by_priority() -> Dict[str, List[Dict]]:
    """Get tasks grouped by priority."""
    result = subprocess.run(["dstask", "show-open"], capture_output=True, text=True)
    tasks = parse_dstask_json(result.stdout)
    
    grouped = {
        "P0": [],
        "P1": [],
        "P2": [],
        "P3": []
    }
    
    for task in tasks:
        priority = task.get("priority", "P2")
        if priority in grouped:
            grouped[priority].append(task)
    
    return grouped

def get_active_tasks() -> List[Dict]:
    """Get currently active tasks."""
    result = subprocess.run(["dstask", "show-active"], capture_output=True, text=True)
    return parse_dstask_json(result.stdout)

def get_completed_today() -> List[Dict]:
    """Get tasks completed today."""
    result = subprocess.run(["dstask", "show-resolved"], capture_output=True, text=True)
    tasks = parse_dstask_json(result.stdout)
    # Filter for today (would need date parsing)
    return tasks[:5]  # Just show last 5 for now

def create_dashboard():
    """Create the main dashboard."""
    # Get data
    tasks_by_priority = get_tasks_by_priority()
    active_tasks = get_active_tasks()
    completed = get_completed_today()
    
    # Create layout
    layout = Layout()
    
    # Header
    header = Panel(
        "[bold cyan]Claude Parser Backlog Dashboard[/bold cyan]\n"
        "[dim]Fully offline, git-backed task management[/dim]",
        box=box.ROUNDED
    )
    
    # Priority breakdown table
    priority_table = Table(title="Tasks by Priority", box=box.SIMPLE)
    priority_table.add_column("Priority", style="cyan", width=10)
    priority_table.add_column("Count", style="magenta", width=8)
    priority_table.add_column("Tasks", style="white")
    
    priority_colors = {
        "P0": "[red]P0 Critical[/red]",
        "P1": "[yellow]P1 High[/yellow]", 
        "P2": "[green]P2 Normal[/green]",
        "P3": "[dim]P3 Low[/dim]"
    }
    
    for priority in ["P0", "P1", "P2", "P3"]:
        tasks = tasks_by_priority[priority]
        if tasks:
            task_summaries = "\n".join([f"• {t['summary'][:40]}..." for t in tasks[:3]])
            if len(tasks) > 3:
                task_summaries += f"\n[dim]... and {len(tasks)-3} more[/dim]"
            priority_table.add_row(
                priority_colors[priority],
                str(len(tasks)),
                task_summaries
            )
    
    # Active tasks table
    active_table = Table(title="🔄 Active Tasks", box=box.SIMPLE)
    active_table.add_column("ID", style="cyan", width=5)
    active_table.add_column("Task", style="yellow")
    active_table.add_column("Tags", style="dim")
    
    if active_tasks:
        for task in active_tasks:
            tags = ", ".join(task.get("tags", []))
            active_table.add_row(
                str(task["id"]),
                task["summary"][:50],
                tags
            )
    else:
        active_table.add_row("", "[dim]No active tasks[/dim]", "")
    
    # Stats panel
    total_tasks = sum(len(tasks) for tasks in tasks_by_priority.values())
    critical_count = len(tasks_by_priority["P0"])
    
    stats = Panel(
        f"[bold]📊 Statistics[/bold]\n\n"
        f"Total Open: {total_tasks}\n"
        f"Critical (P0): {critical_count}\n"
        f"Active: {len(active_tasks)}\n"
        f"Completed Today: {len(completed)}",
        box=box.ROUNDED
    )
    
    # Commands panel
    commands = Panel(
        "[bold]🤖 Claude Code Commands[/bold]\n\n"
        "[cyan]dstask add[/cyan] \"Task\" +tag P0\n"
        "[cyan]dstask 2 start[/cyan] - Start task 2\n"
        "[cyan]dstask 2 done[/cyan] - Complete task 2\n"
        "[cyan]dstask 2 note[/cyan] - Add notes\n"
        "[cyan]dstask next[/cyan] - Show priorities\n"
        "[cyan]dstask sync[/cyan] - Git sync",
        box=box.ROUNDED
    )
    
    # Display everything
    console.print(header)
    console.print()
    console.print(priority_table)
    console.print()
    console.print(active_table)
    console.print()
    
    # Side by side stats and commands
    console.print(stats)
    console.print(commands)
    
    # Next actions
    console.print("\n[bold yellow]🎯 Next Actions:[/bold yellow]")
    if tasks_by_priority["P0"]:
        for task in tasks_by_priority["P0"][:3]:
            console.print(f"  [red]• #{task['id']}:[/red] {task['summary']}")
    elif tasks_by_priority["P1"]:
        for task in tasks_by_priority["P1"][:3]:
            console.print(f"  [yellow]• #{task['id']}:[/yellow] {task['summary']}")

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "watch":
        # Live update mode
        from time import sleep
        with Live(create_dashboard(), refresh_per_second=0.5) as live:
            while True:
                sleep(5)
                live.update(create_dashboard())
    else:
        create_dashboard()

if __name__ == "__main__":
    main()
