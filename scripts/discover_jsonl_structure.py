#!/usr/bin/env python3
"""
JSONL Structure Discovery Tool - Complete Analysis
Discovers ALL keys, nested structures, and variations in Claude Code JSONL files.
Uses streaming to handle huge files without choking.
"""

import orjson
from pathlib import Path
from typing import Dict, Set, Any, List, Union
from collections import defaultdict
import mmap
import random
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.progress import track
from rich import print as rprint
import typer
from dataclasses import dataclass, field
import hashlib

app = typer.Typer(help="Discover complete JSONL structure from Claude Code files")
console = Console()

@dataclass
class FieldInfo:
    """Information about a field."""
    types: Set[str] = field(default_factory=set)
    samples: List[Any] = field(default_factory=list)
    occurrences: int = 0
    nullable: bool = False
    array_types: Set[str] = field(default_factory=set)
    object_keys: Set[str] = field(default_factory=set)
    unique_values: Set[str] = field(default_factory=set)  # For enums
    min_value: Any = None
    max_value: Any = None

class StructureDiscoverer:
    """Discovers complete JSONL structure including all variations."""
    
    def __init__(self):
        self.fields: Dict[str, FieldInfo] = defaultdict(FieldInfo)
        self.message_types = defaultdict(int)
        self.content_block_types = defaultdict(int)
        self.tool_names = defaultdict(int)
        self.usage_fields = defaultdict(FieldInfo)
        self.model_names = set()
        self.session_ids = set()
        self.versions = set()
        self.lines_processed = 0
        self.files_processed = 0
        
    def analyze_value(self, path: str, value: Any, parent_type: str = "root"):
        """Recursively analyze value structure."""
        info = self.fields[path]
        info.occurrences += 1
        
        if value is None:
            info.nullable = True
            info.types.add("null")
            return
            
        value_type = type(value).__name__
        info.types.add(value_type)
        
        # Track samples (max 5 unique samples per type)
        if len(info.samples) < 5:
            if isinstance(value, str) and len(value) > 100:
                sample = value[:100] + "..."
            else:
                sample = value
            if sample not in info.samples:
                info.samples.append(sample)
        
        # Type-specific analysis
        if isinstance(value, bool):
            info.types.add("boolean")
            
        elif isinstance(value, (int, float)):
            info.types.add("number")
            # Track min/max
            if info.min_value is None or value < info.min_value:
                info.min_value = value
            if info.max_value is None or value > info.max_value:
                info.max_value = value
                
        elif isinstance(value, str):
            info.types.add("string")
            # Track unique values for potential enums
            if len(value) < 50 and len(info.unique_values) < 20:
                info.unique_values.add(value)
            
            # Special handling for specific fields
            if path == "sessionId":
                self.session_ids.add(value)
            elif path == "version":
                self.versions.add(value)
            elif path == "message.model":
                self.model_names.add(value)
                
        elif isinstance(value, list):
            info.types.add("array")
            # Analyze array items
            for idx, item in enumerate(value[:20]):  # Sample first 20 items
                item_type = type(item).__name__
                info.array_types.add(item_type)
                
                if isinstance(item, dict):
                    # Track object keys in arrays
                    info.object_keys.update(item.keys())
                    
                    # Recursively analyze array items
                    for key, val in item.items():
                        self.analyze_value(f"{path}[].{key}", val, "array_item")
                    
                    # Special handling for content blocks
                    if "type" in item:
                        block_type = item.get("type")
                        if "content" in path:
                            self.content_block_types[block_type] += 1
                        
                        # Analyze block-specific fields
                        if block_type == "tool_use":
                            if "name" in item:
                                self.tool_names[item["name"]] += 1
                            if "input" in item:
                                self.analyze_value(f"{path}[type={block_type}].input", item["input"], "tool_input")
                                
                        elif block_type == "text":
                            if "text" in item:
                                self.analyze_value(f"{path}[type={block_type}].text", item["text"], "text_content")
                                
                elif not isinstance(item, dict):
                    # For primitive arrays, sample values
                    self.analyze_value(f"{path}[]", item, "array_element")
                    
        elif isinstance(value, dict):
            info.types.add("object")
            info.object_keys.update(value.keys())
            
            # Recursively analyze nested structure
            for key, val in value.items():
                child_path = f"{path}.{key}" if path else key
                self.analyze_value(child_path, val, "object")
                
                # Special handling for usage field
                if path == "message" and key == "usage" and isinstance(val, dict):
                    for usage_key, usage_val in val.items():
                        usage_info = self.usage_fields[usage_key]
                        usage_info.occurrences += 1
                        if isinstance(usage_val, (int, float)):
                            usage_info.types.add("number")
                            if len(usage_info.samples) < 5:
                                usage_info.samples.append(usage_val)
    
    def process_line(self, line: bytes) -> bool:
        """Process a single JSONL line. Returns True if successful."""
        try:
            data = orjson.loads(line)
            self.lines_processed += 1
            
            # Track message type
            if "type" in data:
                self.message_types[data["type"]] += 1
            
            # Analyze all top-level fields
            for key, value in data.items():
                self.analyze_value(key, value)
            
            return True
            
        except orjson.JSONDecodeError:
            return False
        except Exception as e:
            console.print(f"[yellow]Error processing line: {e}[/yellow]")
            return False
    
    def process_file(self, file_path: Path, sample_rate: float = 1.0) -> int:
        """Process a single file. Returns number of lines processed."""
        lines_in_file = 0
        
        try:
            file_size = file_path.stat().st_size
            
            # Use different strategies based on file size
            if file_size < 10_000_000:  # < 10MB - process all
                with open(file_path, 'rb') as f:
                    for line in f:
                        if line.strip():
                            if self.process_line(line):
                                lines_in_file += 1
                                
            else:  # Large file - use mmap and sampling
                with open(file_path, 'rb') as f:
                    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
                        # Count total lines
                        total_lines = sum(1 for _ in iter(mmapped.readline, b""))
                        mmapped.seek(0)
                        
                        # Calculate sample
                        sample_size = max(500, int(total_lines * sample_rate))
                        lines_to_sample = random.sample(range(total_lines), min(sample_size, total_lines))
                        lines_to_sample.sort()
                        
                        current_line = 0
                        for line_num in lines_to_sample:
                            # Skip to target line
                            while current_line < line_num:
                                mmapped.readline()
                                current_line += 1
                            
                            line = mmapped.readline()
                            if line.strip():
                                if self.process_line(line):
                                    lines_in_file += 1
                            current_line += 1
            
            self.files_processed += 1
            return lines_in_file
            
        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")
            return 0
    
    def generate_complete_structure(self) -> Dict[str, Any]:
        """Generate complete structure dictionary."""
        structure = {
            "core_fields": {},
            "message_types": dict(self.message_types),
            "content_block_types": dict(self.content_block_types),
            "tool_names": dict(self.tool_names),
            "usage_fields": {},
            "statistics": {
                "files_processed": self.files_processed,
                "lines_processed": self.lines_processed,
                "unique_sessions": len(self.session_ids),
                "versions_seen": list(self.versions),
                "models_seen": list(self.model_names)
            }
        }
        
        # Process fields
        for path, info in self.fields.items():
            if "." not in path and "[" not in path:  # Root fields
                field_data = {
                    "types": list(info.types),
                    "nullable": info.nullable,
                    "occurrences": info.occurrences,
                    "samples": info.samples[:3]
                }
                
                # Add type-specific info
                if info.unique_values and len(info.unique_values) < 10:
                    field_data["possible_values"] = list(info.unique_values)
                if info.min_value is not None:
                    field_data["range"] = {"min": info.min_value, "max": info.max_value}
                if info.array_types:
                    field_data["array_types"] = list(info.array_types)
                if info.object_keys:
                    field_data["object_keys"] = list(info.object_keys)
                
                structure["core_fields"][path] = field_data
        
        # Process usage fields
        for field, info in self.usage_fields.items():
            structure["usage_fields"][field] = {
                "types": list(info.types),
                "occurrences": info.occurrences,
                "samples": info.samples[:3]
            }
        
        return structure
    
    def generate_typescript(self) -> str:
        """Generate complete TypeScript definitions."""
        lines = [
            "// Complete Claude Code JSONL Structure",
            "// Auto-discovered from real files",
            ""
        ]
        
        # Main message interface
        lines.append("interface ClaudeMessage {")
        
        for path, info in sorted(self.fields.items()):
            if "." not in path and "[" not in path:  # Root fields
                # Determine TypeScript type
                ts_types = []
                for t in info.types:
                    if t in ["str", "string"]:
                        ts_types.append("string")
                    elif t in ["int", "float", "number"]:
                        ts_types.append("number")
                    elif t == "bool":
                        ts_types.append("boolean")
                    elif t == "dict":
                        ts_types.append("object")
                    elif t == "list":
                        ts_types.append("any[]")
                    elif t == "NoneType":
                        continue
                    else:
                        ts_types.append(t)
                
                # Add null if nullable
                if info.nullable:
                    ts_types.append("null")
                
                # Build type string
                type_str = " | ".join(ts_types) if ts_types else "any"
                
                # Add enum if possible
                if info.unique_values and len(info.unique_values) <= 8:
                    type_str = " | ".join(f'"{v}"' for v in sorted(info.unique_values))
                
                # Add comment with samples
                if info.samples:
                    samples_str = ", ".join(str(s)[:30] for s in info.samples[:2])
                    lines.append(f"  // Examples: {samples_str}")
                
                # Add field
                optional = "?" if info.nullable or info.occurrences < self.lines_processed else ""
                lines.append(f"  {path}{optional}: {type_str};")
        
        lines.append("}")
        lines.append("")
        
        # Usage interface
        if self.usage_fields:
            lines.append("interface UsageInfo {")
            for field in sorted(self.usage_fields.keys()):
                lines.append(f"  {field}?: number;")
            lines.append("}")
            lines.append("")
        
        # Content block types
        if self.content_block_types:
            lines.append("type ContentBlockType =")
            for block_type in sorted(self.content_block_types.keys()):
                lines.append(f'  | "{block_type}"')
            lines[-1] = lines[-1] + ";"
            lines.append("")
        
        # Tool names enum
        if self.tool_names:
            lines.append("type ToolName =")
            for tool in sorted(self.tool_names.keys()):
                lines.append(f'  | "{tool}"')
            lines[-1] = lines[-1] + ";"
        
        return "\n".join(lines)
    
    def generate_markdown_report(self) -> str:
        """Generate comprehensive markdown documentation."""
        lines = [
            "# Complete JSONL Structure Analysis",
            "",
            f"Analyzed {self.files_processed} files, {self.lines_processed:,} lines",
            "",
            "## Message Types Distribution",
            ""
        ]
        
        # Message types table
        lines.append("| Type | Count | Percentage |")
        lines.append("|------|-------|------------|")
        total = sum(self.message_types.values())
        for msg_type, count in sorted(self.message_types.items(), key=lambda x: -x[1]):
            pct = (count / total * 100) if total > 0 else 0
            lines.append(f"| {msg_type} | {count:,} | {pct:.1f}% |")
        
        lines.append("")
        lines.append("## Core Fields")
        lines.append("")
        
        # Core fields
        for path, info in sorted(self.fields.items()):
            if "." not in path and "[" not in path:
                lines.append(f"### `{path}`")
                lines.append(f"- **Types**: {', '.join(info.types)}")
                lines.append(f"- **Nullable**: {info.nullable}")
                lines.append(f"- **Occurrences**: {info.occurrences:,}/{self.lines_processed:,} ({info.occurrences/self.lines_processed*100:.1f}%)")
                
                if info.unique_values and len(info.unique_values) <= 10:
                    lines.append(f"- **Possible values**: {', '.join(sorted(info.unique_values))}")
                
                if info.samples:
                    lines.append("- **Examples**:")
                    for sample in info.samples[:3]:
                        sample_str = str(sample)[:100]
                        lines.append(f"  - `{sample_str}`")
                
                lines.append("")
        
        # Usage fields
        if self.usage_fields:
            lines.append("## Usage Fields (Token Tracking)")
            lines.append("")
            lines.append("| Field | Occurrences | Sample Values |")
            lines.append("|-------|-------------|---------------|")
            for field, info in sorted(self.usage_fields.items()):
                samples = ", ".join(str(s) for s in info.samples[:3])
                lines.append(f"| {field} | {info.occurrences:,} | {samples} |")
            lines.append("")
        
        # Content blocks
        if self.content_block_types:
            lines.append("## Content Block Types")
            lines.append("")
            lines.append("| Type | Count |")
            lines.append("|------|-------|")
            for block_type, count in sorted(self.content_block_types.items(), key=lambda x: -x[1]):
                lines.append(f"| {block_type} | {count:,} |")
            lines.append("")
        
        # Tools
        if self.tool_names:
            lines.append("## Tool Usage")
            lines.append("")
            lines.append("| Tool | Usage Count |")
            lines.append("|------|-------------|")
            for tool, count in sorted(self.tool_names.items(), key=lambda x: -x[1])[:20]:
                lines.append(f"| {tool} | {count:,} |")
        
        return "\n".join(lines)

@app.command()
def analyze(
    directory: Path = typer.Argument(
        Path("/Users/ali/.claude/projects"),
        help="Directory containing Claude projects"
    ),
    output_dir: Path = typer.Option(
        Path("/Users/ali/.claude/projects/claude-parser/docs"),
        "--output", "-o",
        help="Output directory for results"
    ),
    limit: int = typer.Option(
        0,
        "--limit", "-l",
        help="Limit number of files to process (0 = all)"
    ),
    sample_rate: float = typer.Option(
        1.0,
        "--sample", "-s",
        help="Sampling rate for large files (0.1-1.0)"
    )
):
    """Analyze all JSONL files and discover complete structure."""
    
    discoverer = StructureDiscoverer()
    
    # Find all JSONL files
    pattern = "**/*.jsonl" if directory.is_dir() else "*.jsonl"
    files = list(directory.glob(pattern))
    
    if limit > 0:
        files = files[:limit]
    
    if not files:
        console.print("[red]No JSONL files found![/red]")
        return
    
    console.print(f"[bold green]Found {len(files)} JSONL files to analyze[/bold green]")
    
    # Process files with progress bar
    for file_path in track(files, description="Analyzing files..."):
        lines = discoverer.process_file(file_path, sample_rate)
        if lines > 0:
            console.print(f"[dim]Processed {file_path.name}: {lines} lines[/dim]")
    
    # Generate outputs
    console.print("\n[bold yellow]Generating reports...[/bold yellow]")
    
    # Save complete structure as JSON
    structure = discoverer.generate_complete_structure()
    structure_file = output_dir / "JSONL_COMPLETE_STRUCTURE.json"
    structure_file.write_text(orjson.dumps(structure, option=orjson.OPT_INDENT_2).decode())
    console.print(f"✅ Complete structure saved to {structure_file}")
    
    # Save TypeScript definitions
    typescript = discoverer.generate_typescript()
    ts_file = output_dir / "claude-message.d.ts"
    ts_file.write_text(typescript)
    console.print(f"✅ TypeScript definitions saved to {ts_file}")
    
    # Save markdown report
    markdown = discoverer.generate_markdown_report()
    md_file = output_dir / "JSONL_STRUCTURE_COMPLETE.md"
    md_file.write_text(markdown)
    console.print(f"✅ Markdown report saved to {md_file}")
    
    # Update the existing JSONL-STRUCTURE.md with discoveries
    existing_file = output_dir / "JSONL-STRUCTURE.md"
    if existing_file.exists():
        original = existing_file.read_text()
        
        # Append discoveries
        updated = original + "\n\n---\n\n## Auto-Discovered Structure\n\n" + markdown
        
        backup = output_dir / "JSONL-STRUCTURE.md.backup"
        backup.write_text(original)
        existing_file.write_text(updated)
        console.print(f"✅ Updated {existing_file} (backup at {backup})")
    
    # Print summary
    console.print("\n[bold cyan]Analysis Complete![/bold cyan]")
    console.print(f"📊 Files processed: {discoverer.files_processed}")
    console.print(f"📝 Lines analyzed: {discoverer.lines_processed:,}")
    console.print(f"🔤 Message types found: {len(discoverer.message_types)}")
    console.print(f"🛠️ Tools discovered: {len(discoverer.tool_names)}")
    console.print(f"📈 Usage fields found: {len(discoverer.usage_fields)}")
    console.print(f"🎯 Unique sessions: {len(discoverer.session_ids)}")
    
    # Show usage fields if found
    if discoverer.usage_fields:
        console.print("\n[bold green]Token tracking fields discovered![/bold green]")
        for field, info in discoverer.usage_fields.items():
            console.print(f"  • {field}: {info.samples[:3]}")

if __name__ == "__main__":
    app()