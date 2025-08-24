#!/usr/bin/env python3
"""
Simple JSONL structure discovery without typer.
"""

import orjson
from pathlib import Path
from collections import defaultdict
import sys
from rich.console import Console
from rich.progress import track

console = Console()

class StructureDiscoverer:
    def __init__(self):
        self.fields = defaultdict(lambda: {
            'types': set(),
            'samples': [],
            'count': 0,
            'nullable': False
        })
        self.message_types = defaultdict(int)
        self.content_blocks = defaultdict(int)
        self.tools = defaultdict(int)
        self.usage_fields = defaultdict(lambda: {'count': 0, 'samples': []})
        self.lines_processed = 0
        
    def analyze_value(self, path, value, depth=0):
        """Recursively analyze structure."""
        if depth > 10:  # Prevent infinite recursion
            return
            
        info = self.fields[path]
        info['count'] += 1
        
        if value is None:
            info['nullable'] = True
            info['types'].add('null')
            return
            
        type_name = type(value).__name__
        info['types'].add(type_name)
        
        # Store samples
        if len(info['samples']) < 3:
            if isinstance(value, str) and len(value) > 100:
                sample = value[:100] + "..."
            else:
                sample = value
            if sample not in info['samples']:
                info['samples'].append(sample)
        
        # Handle different types
        if isinstance(value, dict):
            for key, val in value.items():
                child_path = f"{path}.{key}" if path else key
                self.analyze_value(child_path, val, depth + 1)
                
                # Special handling for usage
                if key == "usage" and isinstance(val, dict):
                    for usage_key, usage_val in val.items():
                        self.usage_fields[usage_key]['count'] += 1
                        if len(self.usage_fields[usage_key]['samples']) < 3:
                            self.usage_fields[usage_key]['samples'].append(usage_val)
                            
        elif isinstance(value, list):
            for item in value[:10]:  # Sample first 10 items
                if isinstance(item, dict):
                    # Track content block types
                    if "type" in item:
                        block_type = item.get("type")
                        self.content_blocks[block_type] += 1
                        
                        # Track tool names
                        if block_type == "tool_use" and "name" in item:
                            self.tools[item["name"]] += 1
                        
                        # Analyze block structure
                        for key, val in item.items():
                            self.analyze_value(f"{path}[].{key}", val, depth + 1)
                else:
                    self.analyze_value(f"{path}[]", item, depth + 1)
    
    def process_line(self, line):
        """Process single JSONL line."""
        try:
            data = orjson.loads(line)
            self.lines_processed += 1
            
            # Track message type
            if "type" in data:
                self.message_types[data["type"]] += 1
            
            # Analyze all fields
            for key, value in data.items():
                self.analyze_value(key, value)
            
            return True
        except Exception as e:
            return False
    
    def process_file(self, file_path):
        """Process a JSONL file."""
        count = 0
        try:
            with open(file_path, 'rb') as f:
                for line in f:
                    if line.strip():
                        if self.process_line(line):
                            count += 1
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")
        return count

def main():
    if len(sys.argv) < 2:
        print("Usage: python discover_structure_simple.py <directory_or_file>")
        sys.exit(1)
    
    path = Path(sys.argv[1])
    discoverer = StructureDiscoverer()
    
    # Find files
    if path.is_file():
        files = [path]
    else:
        files = list(path.glob("*.jsonl"))
        if not files:  # Try subdirectories
            files = list(path.glob("**/*.jsonl"))
    
    # Limit to first 10 files for testing
    files = files[:10]
    
    if not files:
        console.print("[red]No JSONL files found![/red]")
        return
    
    console.print(f"[bold green]Analyzing {len(files)} files...[/bold green]")
    
    # Process files
    for file_path in track(files, description="Processing..."):
        count = discoverer.process_file(file_path)
        if count > 0:
            console.print(f"[dim]{file_path.name}: {count} lines[/dim]")
    
    # Output results
    console.print(f"\n[bold cyan]Results:[/bold cyan]")
    console.print(f"Lines processed: {discoverer.lines_processed:,}")
    console.print(f"Message types: {dict(discoverer.message_types)}")
    
    # Core fields
    console.print("\n[bold]Core Fields:[/bold]")
    for path, info in sorted(discoverer.fields.items()):
        if "." not in path and "[" not in path:
            types = ", ".join(info['types'])
            console.print(f"  {path}: {types} ({info['count']} occurrences)")
            if info['samples']:
                console.print(f"    Sample: {str(info['samples'][0])[:50]}")
    
    # Usage fields
    if discoverer.usage_fields:
        console.print("\n[bold green]Token Usage Fields Found![/bold green]")
        for field, info in discoverer.usage_fields.items():
            console.print(f"  {field}: {info['samples'][:3]}")
    
    # Content blocks
    if discoverer.content_blocks:
        console.print("\n[bold]Content Block Types:[/bold]")
        for block_type, count in discoverer.content_blocks.items():
            console.print(f"  {block_type}: {count}")
    
    # Tools
    if discoverer.tools:
        console.print("\n[bold]Tools Used:[/bold]")
        for tool, count in sorted(discoverer.tools.items(), key=lambda x: -x[1])[:10]:
            console.print(f"  {tool}: {count}")
    
    # Save complete structure
    output_file = Path("/Users/ali/.claude/projects/claude-parser/docs/JSONL_STRUCTURE_DISCOVERED.json")
    structure = {
        "lines_processed": discoverer.lines_processed,
        "message_types": dict(discoverer.message_types),
        "fields": {
            path: {
                "types": list(info['types']),
                "nullable": info['nullable'],
                "count": info['count'],
                "samples": info['samples'][:3]
            }
            for path, info in discoverer.fields.items()
        },
        "usage_fields": dict(discoverer.usage_fields),
        "content_blocks": dict(discoverer.content_blocks),
        "tools": dict(discoverer.tools)
    }
    
    output_file.write_text(orjson.dumps(structure, option=orjson.OPT_INDENT_2).decode())
    console.print(f"\n[green]✅ Complete structure saved to {output_file}[/green]")

if __name__ == "__main__":
    main()