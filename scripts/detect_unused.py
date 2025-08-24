#!/usr/bin/env python3
"""
Detect unused Python files in the codebase.
Files that are not imported anywhere are likely dead code.
"""
import ast
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def get_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all imports from a Python file."""
    imports = set()
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                    # Also add the full import paths
                    for alias in node.names:
                        if node.module:
                            imports.add(f"{node.module}.{alias.name}")
    except Exception as e:
        print(f"{YELLOW}Warning: Could not parse {file_path}: {e}{RESET}")
    
    return imports

def get_all_python_files(root_dir: Path) -> List[Path]:
    """Get all Python files in the project."""
    files = []
    for pattern in ["*.py"]:
        files.extend(root_dir.rglob(pattern))
    
    # Filter out __pycache__, venv, .git, etc.
    filtered = []
    for f in files:
        path_str = str(f)
        if any(skip in path_str for skip in ["__pycache__", "venv", ".git", "build", "dist", ".egg"]):
            continue
        filtered.append(f)
    
    return filtered

def module_path_from_file(file_path: Path, root_dir: Path) -> str:
    """Convert file path to module import path."""
    # Get relative path from root
    try:
        relative = file_path.relative_to(root_dir)
        # Remove .py extension and convert to module path
        module_path = str(relative.with_suffix(""))
        # Replace path separators with dots
        module_path = module_path.replace("/", ".")
        module_path = module_path.replace("\\", ".")
        return module_path
    except ValueError:
        # File is not under root_dir
        return str(file_path.stem)

def analyze_usage(root_dir: Path = Path(".")) -> Tuple[Dict[Path, Set[Path]], List[Path]]:
    """Analyze which files are used by which other files."""
    all_files = get_all_python_files(root_dir)
    
    # Build import graph
    file_imports: Dict[Path, Set[str]] = {}
    for file_path in all_files:
        file_imports[file_path] = get_imports_from_file(file_path)
    
    # Map module names to file paths
    module_to_file: Dict[str, Path] = {}
    for file_path in all_files:
        module_path = module_path_from_file(file_path, root_dir)
        module_to_file[module_path] = file_path
        
        # Also add parent module paths (for __init__.py files)
        parts = module_path.split(".")
        for i in range(len(parts)):
            partial = ".".join(parts[:i+1])
            if partial not in module_to_file:
                # Check if __init__.py exists
                init_path = root_dir / Path(*parts[:i+1]) / "__init__.py"
                if init_path.exists():
                    module_to_file[partial] = init_path
    
    # Build usage graph: file -> set of files that import it
    used_by: Dict[Path, Set[Path]] = {f: set() for f in all_files}
    
    for file_path, imports in file_imports.items():
        for imp in imports:
            # Try exact match first
            if imp in module_to_file:
                used_by[module_to_file[imp]].add(file_path)
            else:
                # Try partial matches (for from X import Y statements)
                for module_name, module_file in module_to_file.items():
                    if imp.startswith(module_name):
                        used_by[module_file].add(file_path)
    
    # Find unused files
    unused = []
    for file_path in all_files:
        # Skip test files, scripts, and __init__.py files
        path_str = str(file_path)
        if any(skip in path_str for skip in ["test", "__init__.py", "scripts/", "setup.py"]):
            continue
        
        # Check if file is imported anywhere
        if len(used_by[file_path]) == 0:
            # Special case: main package file or entry points
            if file_path.name == "__main__.py":
                continue
            if str(file_path) == "claude_parser/__init__.py":
                continue  # Main package init
                
            unused.append(file_path)
    
    return used_by, unused

def categorize_file(file_path: Path) -> str:
    """Categorize a file based on its location and purpose."""
    path_str = str(file_path)
    
    if "scripts/" in path_str:
        return "script"
    elif "test" in path_str:
        return "test"
    elif "__init__.py" in file_path.name:
        return "package"
    elif "domain/" in path_str:
        return "domain"
    elif "infrastructure/" in path_str:
        return "infrastructure"
    elif "application/" in path_str:
        return "application"
    elif "hooks/" in path_str:
        return "hooks"
    elif "watch/" in path_str:
        return "watch"
    elif "discovery/" in path_str:
        return "discovery"
    else:
        return "other"

def main():
    """Main function to detect unused files."""
    print(f"\n{BLUE}═══ Unused File Detection ═══{RESET}\n")
    
    root_dir = Path(".")
    used_by, unused = analyze_usage(root_dir)
    
    if not unused:
        print(f"{GREEN}✓ No unused files detected!{RESET}\n")
        return 0
    
    print(f"{RED}✗ Found {len(unused)} unused files:{RESET}\n")
    
    # Group by category
    categorized: Dict[str, List[Path]] = {}
    for file_path in unused:
        category = categorize_file(file_path)
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(file_path)
    
    # Display unused files by category
    for category, files in sorted(categorized.items()):
        print(f"{YELLOW}{category.upper()} FILES:{RESET}")
        for file_path in files:
            print(f"  {RED}→{RESET} {file_path}")
            
            # Check if it has violations too
            # This helps prioritize what to fix or remove
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    has_violations = any(pattern in content for pattern in [
                        "for ", "while ", ".append(", "[x for x in"
                    ])
                    if has_violations:
                        print(f"    {YELLOW}⚠ Has 95/5 violations - consider removing{RESET}")
            except:
                pass
        print()
    
    print(f"{YELLOW}═══ Recommendations ═══{RESET}\n")
    print(f"1. {YELLOW}REMOVE{RESET}: Delete truly unused files")
    print(f"2. {YELLOW}INTEGRATE{RESET}: If file should be used, properly import it")
    print(f"3. {YELLOW}MOVE TO SCRIPTS{RESET}: If it's a standalone utility, move to scripts/")
    print(f"4. {YELLOW}MOVE TO TOOLS{RESET}: If it's a development tool, create tools/ directory")
    print()
    
    print(f"{RED}╔══════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}║  🚫 UNUSED FILES DETECTED - CLEAN UP REQUIRED 🚫            ║{RESET}")
    print(f"{RED}╚══════════════════════════════════════════════════════════════╝{RESET}\n")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())