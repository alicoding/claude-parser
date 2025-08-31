#!/usr/bin/env python3
"""
Codebase Inventory Generator for AI/LLM Context.

Uses AST to extract comprehensive codebase structure into hierarchical JSON.
Follows LIBRARY_FIRST_RULE.md and 95/5 principle.
"""

import ast
from pathlib import Path
from typing import Dict, Any, Optional
from typing_extensions import Annotated
import orjson
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich import box
import typer
from toolz import pipe, map as toolz_map, filter as toolz_filter, groupby

app = typer.Typer(help="Generate AI-friendly codebase inventory")
console = Console()


class CodebaseAnalyzer:
    """AST-based codebase analyzer for inventory generation."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.console = Console()

    def extract_file_inventory(self, filepath: Path) -> Dict[str, Any]:
        """Extract inventory from a single Python file using AST."""
        try:
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(filepath))

            # Get relative path for cleaner display
            relative_path = filepath.relative_to(self.root_dir)

            inventory = {
                "file": str(relative_path),
                "path": str(filepath),
                "module_docstring": ast.get_docstring(tree),
                "imports": [],
                "functions": [],
                "classes": [],
                "constants": [],
                "size": {
                    "lines": len(source.splitlines()),
                    "bytes": len(source.encode()),
                },
            }

            # Extract all nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        inventory["imports"].append(
                            {"module": alias.name, "alias": alias.asname}
                        )
                elif isinstance(node, ast.ImportFrom):
                    inventory["imports"].append(
                        {
                            "module": node.module or "",
                            "from": True,
                            "names": [n.name for n in node.names],
                        }
                    )

            # Extract top-level definitions
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function(node)
                    inventory["functions"].append(func_info)
                elif isinstance(node, ast.ClassDef):
                    class_info = self._extract_class(node)
                    inventory["classes"].append(class_info)
                elif isinstance(node, ast.Assign):
                    # Extract module-level constants
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            inventory["constants"].append(target.id)

            return inventory

        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not parse {filepath}: {e}[/yellow]"
            )
            return None

    def _extract_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Extract function information from AST node."""
        # Build signature
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += (
                    f": {ast.unparse(arg.annotation)}"
                    if hasattr(ast, "unparse")
                    else ""
                )
            args.append(arg_str)

        # Get return type
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, "unparse") else "..."

        return {
            "name": node.name,
            "signature": f"({', '.join(args)})" + (f" -> {returns}" if returns else ""),
            "docstring": ast.get_docstring(node),
            "decorators": [
                ast.unparse(d) if hasattr(ast, "unparse") else "..."
                for d in node.decorator_list
            ],
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "line_number": node.lineno,
        }

    def _extract_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract class information from AST node."""
        class_info = {
            "name": node.name,
            "bases": [],
            "docstring": ast.get_docstring(node),
            "methods": [],
            "attributes": [],
            "properties": [],
            "class_variables": [],
            "line_number": node.lineno,
        }

        # Extract base classes
        for base in node.bases:
            if isinstance(base, ast.Name):
                class_info["bases"].append(base.id)
            elif hasattr(ast, "unparse"):
                class_info["bases"].append(ast.unparse(base))

        # Extract class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function(item)

                # Check if it's a property
                if any(
                    isinstance(d, ast.Name) and d.id == "property"
                    for d in item.decorator_list
                ):
                    class_info["properties"].append(method_info["name"])
                else:
                    class_info["methods"].append(method_info)

            elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                # Type-annotated class variable
                class_info["class_variables"].append(
                    {
                        "name": item.target.id,
                        "type": ast.unparse(item.annotation)
                        if hasattr(ast, "unparse")
                        else "...",
                    }
                )
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info["attributes"].append(target.id)

        return class_info

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze entire codebase and generate hierarchical inventory."""
        self.console.print(f"[cyan]Analyzing codebase: {self.root_dir}[/cyan]")

        # Collect all Python files
        python_files = list(self.root_dir.rglob("*.py"))

        # Filter out common exclusions
        excluded_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "venv",
            ".venv",
            "build",
            "dist",
        }
        python_files = [
            f for f in python_files if not any(ex in f.parts for ex in excluded_dirs)
        ]

        self.console.print(f"[dim]Found {len(python_files)} Python files[/dim]")

        # Extract inventory for each file
        all_inventories = pipe(
            python_files,
            lambda files: toolz_map(self.extract_file_inventory, files),
            lambda invs: toolz_filter(lambda x: x is not None, invs),
            list,
        )

        # Group by package/module structure
        def get_package(inv):
            """Extract package name from file path."""
            parts = Path(inv["file"]).parts
            if len(parts) > 1 and parts[0] == "claude_parser":
                return "claude_parser"
            elif len(parts) > 0:
                return parts[0]
            return "root"

        grouped = groupby(get_package, all_inventories)

        # Build hierarchical structure
        inventory = {
            "project": str(self.root_dir.name),
            "root_path": str(self.root_dir),
            "summary": {
                "total_files": len(all_inventories),
                "total_lines": sum(inv["size"]["lines"] for inv in all_inventories),
                "total_classes": sum(len(inv["classes"]) for inv in all_inventories),
                "total_functions": sum(
                    len(inv["functions"]) for inv in all_inventories
                ),
            },
            "packages": {},
        }

        # Organize by package
        for package, files in grouped.items():
            files_list = list(files)

            # Further group by subdirectory within package
            if package == "claude_parser":
                subgroups = groupby(
                    lambda inv: self._get_subdomain(inv["file"]), files_list
                )
                inventory["packages"][package] = {"domains": {}}

                for domain, domain_files in subgroups.items():
                    domain_files_list = list(domain_files)
                    inventory["packages"][package]["domains"][domain] = {
                        "responsibility": self._infer_domain_responsibility(domain),
                        "files": domain_files_list,
                        "summary": {
                            "file_count": len(domain_files_list),
                            "class_count": sum(
                                len(f["classes"]) for f in domain_files_list
                            ),
                            "function_count": sum(
                                len(f["functions"]) for f in domain_files_list
                            ),
                        },
                    }
            else:
                inventory["packages"][package] = {
                    "files": files_list,
                    "summary": {
                        "file_count": len(files_list),
                        "class_count": sum(len(f["classes"]) for f in files_list),
                        "function_count": sum(len(f["functions"]) for f in files_list),
                    },
                }

        return inventory

    def _get_subdomain(self, filepath: str) -> str:
        """Extract subdomain from claude_parser file path."""
        parts = Path(filepath).parts
        if len(parts) > 1 and parts[0] == "claude_parser":
            if len(parts) > 2:
                return parts[1]  # Subdirectory like "models", "features", etc.
            return "core"  # Top-level files
        return "other"

    def _infer_domain_responsibility(self, domain: str) -> str:
        """Infer domain responsibility from directory name."""
        responsibilities = {
            "core": "Core functionality and main exports",
            "models": "Data models and domain entities",
            "features": "Feature registry and capability tracking",
            "infrastructure": "Infrastructure and utilities",
            "hooks": "Hook system for Claude Code integration",
            "watch": "File watching and monitoring",
            "navigation": "Message navigation and filtering",
            "transport": "Data transport and serialization",
            "tests": "Test suites and fixtures",
            "scripts": "CLI tools and utilities",
            "docs": "Documentation and specifications",
        }
        return responsibilities.get(domain, f"{domain.title()} domain functionality")


@app.command()
def generate(
    path: Annotated[Path, typer.Argument(help="Path to codebase root")] = Path.cwd(),
    output: Annotated[
        Optional[Path], typer.Option("--output", "-o", help="Output file path")
    ] = None,
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format: json, summary, tree")
    ] = "json",
    show_tree: Annotated[
        bool, typer.Option("--tree", help="Display visual tree")
    ] = False,
    show_stats: Annotated[
        bool, typer.Option("--stats", help="Display statistics table")
    ] = False,
):
    """Generate comprehensive codebase inventory for AI/LLM context."""
    analyzer = CodebaseAnalyzer(path)
    inventory = analyzer.analyze_codebase()

    # Save to file if specified
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            output.write_bytes(orjson.dumps(inventory, option=orjson.OPT_INDENT_2))
            console.print(f"[green]✅ Inventory saved to {output}[/green]")
        elif format == "summary":
            # Generate markdown summary
            summary = generate_markdown_summary(inventory)
            output.write_text(summary)
            console.print(f"[green]✅ Summary saved to {output}[/green]")

    # Display tree visualization
    if show_tree:
        display_tree(inventory)

    # Display statistics
    if show_stats:
        display_stats(inventory)

    # Always show basic summary
    console.print(f"\n[bold cyan]Codebase Inventory Summary:[/bold cyan]")
    console.print(f"  • Total files: {inventory['summary']['total_files']}")
    console.print(f"  • Total lines: {inventory['summary']['total_lines']:,}")
    console.print(f"  • Total classes: {inventory['summary']['total_classes']}")
    console.print(f"  • Total functions: {inventory['summary']['total_functions']}")


def display_tree(inventory: Dict[str, Any]):
    """Display visual tree of codebase structure."""
    tree = Tree(f"[bold cyan]{inventory['project']}[/bold cyan]")

    for package_name, package_data in inventory["packages"].items():
        package_node = tree.add(f"[yellow]{package_name}/[/yellow]")

        if "domains" in package_data:
            for domain_name, domain_data in package_data["domains"].items():
                domain_node = package_node.add(
                    f"[green]{domain_name}/[/green] - {domain_data['responsibility']}"
                )

                # Show file count and key files
                file_count = domain_data["summary"]["file_count"]
                class_count = domain_data["summary"]["class_count"]
                func_count = domain_data["summary"]["function_count"]

                domain_node.add(
                    f"[dim]{file_count} files, {class_count} classes, {func_count} functions[/dim]"
                )
        else:
            # Direct files under package
            file_count = package_data["summary"]["file_count"]
            package_node.add(f"[dim]{file_count} files[/dim]")

    console.print(tree)


def display_stats(inventory: Dict[str, Any]):
    """Display statistics table."""
    table = Table(title="Codebase Statistics", box=box.ROUNDED)
    table.add_column("Domain", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Lines", justify="right")
    table.add_column("Classes", justify="right")
    table.add_column("Functions", justify="right")

    for package_name, package_data in inventory["packages"].items():
        if "domains" in package_data:
            for domain_name, domain_data in package_data["domains"].items():
                # Calculate lines for this domain
                total_lines = sum(f["size"]["lines"] for f in domain_data["files"])

                table.add_row(
                    f"{package_name}/{domain_name}",
                    str(domain_data["summary"]["file_count"]),
                    f"{total_lines:,}",
                    str(domain_data["summary"]["class_count"]),
                    str(domain_data["summary"]["function_count"]),
                )

    console.print(table)


def generate_markdown_summary(inventory: Dict[str, Any]) -> str:
    """Generate markdown summary of inventory."""
    lines = [
        f"# {inventory['project']} - Codebase Inventory",
        "",
        "## Summary",
        f"- **Total Files**: {inventory['summary']['total_files']}",
        f"- **Total Lines**: {inventory['summary']['total_lines']:,}",
        f"- **Total Classes**: {inventory['summary']['total_classes']}",
        f"- **Total Functions**: {inventory['summary']['total_functions']}",
        "",
        "## Package Structure",
        "",
    ]

    for package_name, package_data in inventory["packages"].items():
        lines.append(f"### {package_name}")

        if "domains" in package_data:
            for domain_name, domain_data in package_data["domains"].items():
                lines.append(f"#### {domain_name}")
                lines.append(f"- **Responsibility**: {domain_data['responsibility']}")
                lines.append(f"- **Files**: {domain_data['summary']['file_count']}")
                lines.append(f"- **Classes**: {domain_data['summary']['class_count']}")
                lines.append(
                    f"- **Functions**: {domain_data['summary']['function_count']}"
                )
                lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    app()
