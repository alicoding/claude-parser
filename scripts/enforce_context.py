#!/usr/bin/env python3
"""
Local enforcement of AI context awareness.
Runs BEFORE any code changes to ensure Claude loads context.

This script can be called from:
1. Shell aliases
2. VS Code tasks
3. Makefile targets
4. Direct execution
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import orjson

console = Console()

def check_context_loaded():
    """Check if AI context files have been accessed recently."""
    context_files = [
        Path("docs/ai/AI_CONTEXT.md"),
        Path("docs/ai/CAPABILITY_MATRIX.md"),
        Path("docs/ai/CODEBASE_INVENTORY.json")
    ]
    
    # Check if files exist
    missing = [f for f in context_files if not f.exists()]
    if missing:
        console.print("[red]❌ Missing AI context files:[/red]")
        for f in missing:
            console.print(f"   - {f}")
        return False
    
    # Check if inventory is current
    result = subprocess.run(
        ["python", "scripts/check_inventory_sync.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        console.print("[red]❌ Inventory is out of date![/red]")
        console.print("[yellow]Updating now...[/yellow]")
        
        # Auto-update the inventory
        update_result = subprocess.run(
            ["python", "scripts/codebase_inventory.py", ".", 
             "--output", "docs/ai/CODEBASE_INVENTORY.json"],
            capture_output=True,
            text=True
        )
        
        if update_result.returncode == 0:
            console.print("[green]✅ Inventory updated![/green]")
        else:
            console.print("[red]Failed to update inventory[/red]")
            return False
    
    return True

def display_context_reminder():
    """Display reminder panel for Claude."""
    reminder = """
[bold red]⚠️  CONTEXT REMINDER FOR CLAUDE[/bold red]

You are starting a NEW session with NO memory!
This codebase has:
• 85 classes across 9 domains
• 140 functions already implemented
• 95/5 principle: 95% libraries, 5% glue

[bold yellow]MANDATORY FIRST STEPS:[/bold yellow]
1. Read @docs/ai/AI_CONTEXT.md
2. Check @docs/ai/CAPABILITY_MATRIX.md
3. Search CODEBASE_INVENTORY.json

[bold red]NEVER:[/bold red]
• Create duplicate functionality
• Put code in wrong files
• Build what libraries already do
"""
    
    console.print(Panel(reminder, title="Claude Code Context", border_style="red"))

def show_quick_stats():
    """Show quick codebase stats."""
    inventory_path = Path("docs/ai/CODEBASE_INVENTORY.json")
    if inventory_path.exists():
        data = orjson.loads(inventory_path.read_bytes())
        summary = data.get("summary", {})
        
        console.print("\n[cyan]📊 Current Codebase Stats:[/cyan]")
        console.print(f"   • Total files: {summary.get('total_files', 0)}")
        console.print(f"   • Total classes: {summary.get('total_classes', 0)}")
        console.print(f"   • Total functions: {summary.get('total_functions', 0)}")
        console.print(f"   • Total lines: {summary.get('total_lines', 0)}")

def main():
    """Main enforcement flow."""
    console.print("\n[bold cyan]🔍 Checking AI Context Status...[/bold cyan]\n")
    
    if not check_context_loaded():
        console.print("[red]❌ Context check failed![/red]")
        sys.exit(1)
    
    display_context_reminder()
    show_quick_stats()
    
    console.print("\n[green]✅ Context is ready. Claude can now proceed.[/green]")
    console.print("[dim]Remember: Always check CAPABILITY_MATRIX.md before implementing![/dim]\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
