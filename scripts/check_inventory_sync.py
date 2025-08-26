#!/usr/bin/env python3
"""
Check if codebase inventory is synchronized with actual code.

Exits with 0 if synchronized, 1 if out of date.
Used by pre-commit hooks to enforce documentation updates.
"""

import sys
import subprocess
from pathlib import Path
import orjson
from rich.console import Console
import tempfile

console = Console()


def check_inventory_sync():
    """Check if CODEBASE_INVENTORY.json is up to date."""
    inventory_path = Path("docs/ai/CODEBASE_INVENTORY.json")
    
    # Check if inventory exists
    if not inventory_path.exists():
        console.print("[red]❌ CODEBASE_INVENTORY.json not found![/red]")
        console.print("[yellow]Run: python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json[/yellow]")
        return False
    
    # Read current inventory
    current_inventory = orjson.loads(inventory_path.read_bytes())
    
    # Generate fresh inventory to temp file
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        
    try:
        # Generate fresh inventory
        result = subprocess.run(
            ["python", "scripts/codebase_inventory.py", ".", "--output", str(temp_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print("[red]❌ Failed to generate inventory![/red]")
            console.print(result.stderr)
            return False
        
        # Read fresh inventory
        fresh_inventory = orjson.loads(temp_path.read_bytes())
        
        # Compare key metrics
        current_summary = current_inventory.get("summary", {})
        fresh_summary = fresh_inventory.get("summary", {})
        
        # Check if summaries match
        if current_summary != fresh_summary:
            console.print("[red]❌ Codebase inventory is out of date![/red]")
            console.print("\n[yellow]Differences detected:[/yellow]")
            
            if current_summary.get("total_files") != fresh_summary.get("total_files"):
                console.print(f"  Files: {current_summary.get('total_files')} → {fresh_summary.get('total_files')}")
            if current_summary.get("total_classes") != fresh_summary.get("total_classes"):
                console.print(f"  Classes: {current_summary.get('total_classes')} → {fresh_summary.get('total_classes')}")
            if current_summary.get("total_functions") != fresh_summary.get("total_functions"):
                console.print(f"  Functions: {current_summary.get('total_functions')} → {fresh_summary.get('total_functions')}")
            if current_summary.get("total_lines") != fresh_summary.get("total_lines"):
                console.print(f"  Lines: {current_summary.get('total_lines')} → {fresh_summary.get('total_lines')}")
            
            console.print("\n[yellow]To fix, run:[/yellow]")
            console.print("  python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json")
            console.print("  git add docs/ai/CODEBASE_INVENTORY.json")
            return False
        
        # Deep comparison - check package structure
        current_packages = set(current_inventory.get("packages", {}).keys())
        fresh_packages = set(fresh_inventory.get("packages", {}).keys())
        
        if current_packages != fresh_packages:
            console.print("[red]❌ Package structure changed![/red]")
            if fresh_packages - current_packages:
                console.print(f"  New packages: {fresh_packages - current_packages}")
            if current_packages - fresh_packages:
                console.print(f"  Removed packages: {current_packages - fresh_packages}")
            return False
        
        console.print("[green]✅ Codebase inventory is up to date[/green]")
        return True
        
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


def main():
    """Main entry point."""
    if check_inventory_sync():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
