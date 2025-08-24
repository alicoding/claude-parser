#!/usr/bin/env python3
"""
95/5 Principle Verification - SOLID Version
This script follows its own rules: functional programming with toolz
"""
import sys
import re
import ast
from pathlib import Path
from typing import Tuple, Set, Dict, Any
from toolz import (
    pipe, concat, merge, partition, groupby, count,
    compose, reduce, get_in, valmap
)
from toolz.curried import map as toolz_map, filter as toolz_filter, get
from functools import partial
from more_itertools import flatten

# Import configuration (SOLID: Dependency Inversion)
from verification_config import (
    COLORS, APPROVED_LIBRARIES, FORBIDDEN_IMPORTS,
    FORBIDDEN_PATTERNS, EXEMPTIONS, REQUIRED_TESTS,
    PATHS, EXCLUDED_FILES
)

# ==========================================
# Pure Functions (SOLID: Single Responsibility)
# ==========================================

def print_status(passed: bool, message: str) -> None:
    """Print colored status message."""
    symbol = f"{COLORS['GREEN']}✓{COLORS['RESET']}" if passed else f"{COLORS['RED']}✗{COLORS['RESET']}"
    print(f"{symbol} {message}")

def read_file_safe(path: Path) -> str:
    """Safely read file content."""
    try:
        return path.read_text()
    except:
        return ""

def get_python_files(base_path: str) -> list:
    """Get all Python files from a directory."""
    def has_excluded_pattern(path: Path) -> bool:
        """Check if path contains any excluded pattern."""
        path_str = str(path)
        return pipe(
            EXCLUDED_FILES,
            toolz_map(lambda exc: exc in path_str),
            any
        )
    
    return pipe(
        list(Path(base_path).rglob("*.py")) if Path(base_path).exists() else [],
        toolz_filter(lambda p: not has_excluded_pattern(p)),
        list
    )

def extract_imports_from_line(line: str) -> str:
    """Extract module name from import line."""
    stripped = line.strip()
    if stripped.startswith("import "):
        parts = stripped.split()
        return parts[1].split(".")[0].replace(",", "") if len(parts) >= 2 else ""
    elif stripped.startswith("from "):
        parts = stripped.split()
        return parts[1].split(".")[0] if len(parts) >= 2 else ""
    return ""

def check_line_against_patterns(patterns: list, line: str) -> list:
    """Check if line matches any forbidden pattern."""
    return pipe(
        patterns,
        toolz_map(lambda p: (p[1], p[0]) if re.search(p[0], line) else None),
        toolz_filter(lambda x: x is not None),
        list
    )

def format_violation(file_path: Path, line_no: int, message: str, line: str) -> str:
    """Format a violation message."""
    return f"{file_path}:{line_no} - {message}\n  Found: {line.strip()[:80]}"

# ==========================================
# Check Functions (SOLID: Open/Closed Principle)
# ==========================================

def check_forbidden_imports() -> Tuple[bool, list]:
    """Check for forbidden imports using functional approach."""
    def process_file(file_path: Path) -> list:
        """Process single file for forbidden imports."""
        content = read_file_safe(file_path)
        if not content:
            return []
        
        # Check for exemptions
        exempted_patterns = EXEMPTIONS.get(file_path.name, [])
        
        # Filter patterns based on exemptions
        def is_pattern_exempted(pattern: tuple) -> bool:
            return pipe(
                exempted_patterns,
                toolz_map(lambda ex: ex in pattern[0]),
                any
            )
        
        active_patterns = pipe(
            FORBIDDEN_IMPORTS,
            toolz_filter(lambda p: not is_pattern_exempted(p)),
            list
        )
        
        return pipe(
            enumerate(content.splitlines(), 1),
            toolz_map(lambda x: (x[0], x[1], check_line_against_patterns(active_patterns, x[1]))),
            toolz_filter(lambda x: x[2]),  # Keep only lines with violations
            toolz_map(lambda x: format_violation(file_path, x[0], x[2][0][0], x[1])),
            list
        )
    
    all_files = get_python_files(PATHS["source"]) + get_python_files(PATHS["scripts"])
    violations = pipe(
        all_files,
        toolz_map(process_file),
        concat,
        list
    )
    
    return len(violations) == 0, violations

def check_approved_libraries() -> Tuple[bool, list]:
    """Check that only approved libraries are imported."""
    def process_file(file_path: Path) -> list:
        """Process single file for unapproved libraries."""
        content = read_file_safe(file_path)
        if not content:
            return []
        
        def check_import_line(line_data: tuple) -> str:
            """Check if import is approved."""
            line_no, line = line_data
            module = extract_imports_from_line(line)
            
            if not module:
                return None
            
            # Skip relative and internal imports
            if module.startswith(".") or module.startswith("claude_parser"):
                return None
            
            if module not in APPROVED_LIBRARIES:
                return (
                    f"BLOCKED: {file_path}:{line_no} - UNAPPROVED LIBRARY: {module}\n"
                    f"  Found: {line.strip()}\n"
                    f"  ❌ Add '{module}' to APPROVED_LIBRARIES in verification_config.py"
                )
            
            return None
        
        return pipe(
            enumerate(content.splitlines(), 1),
            toolz_filter(lambda x: x[1].strip().startswith(("import ", "from "))),
            toolz_map(check_import_line),
            toolz_filter(lambda x: x is not None),
            list
        )
    
    all_files = get_python_files(PATHS["source"]) + get_python_files(PATHS["scripts"])
    violations = pipe(
        all_files,
        toolz_map(process_file),
        concat,
        list
    )
    
    return len(violations) == 0, violations

def check_manual_loops() -> Tuple[bool, list]:
    """Check for manual loops and state management."""
    def process_file(file_path: Path) -> list:
        """Process single file for manual loops."""
        content = read_file_safe(file_path)
        if not content:
            return []
        
        def check_line(line_data: tuple) -> list:
            """Check single line for violations."""
            line_no, line = line_data
            
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith('"""'):
                return []
            
            violations = check_line_against_patterns(FORBIDDEN_PATTERNS, line)
            return pipe(
                violations,
                toolz_map(lambda v: format_violation(file_path, line_no, v[0], line)),
                list
            )
        
        return pipe(
            enumerate(content.splitlines(), 1),
            toolz_map(check_line),
            concat,
            list
        )
    
    violations = pipe(
        get_python_files(PATHS["source"]),
        toolz_map(process_file),
        concat,
        list
    )
    
    return len(violations) == 0, violations

def check_95_5_principle() -> Tuple[bool, list]:
    """Check that the API follows 95/5 principle."""
    api_file = Path(PATHS["source"]) / "__init__.py"
    
    if not api_file.exists():
        return False, ["Missing main API file"]
    
    content = read_file_safe(api_file)
    
    issues = pipe(
        [
            ("load" not in content, "Missing simple 'load' function in main API"),
            ("config" in content.lower() and "optional" not in content.lower(), 
             "Basic API seems to require configuration"),
        ],
        toolz_filter(lambda x: x[0]),
        toolz_map(lambda x: x[1]),
        list
    )
    
    return len(issues) == 0, issues

def check_tests_exist() -> Tuple[bool, list]:
    """Check that required test files exist."""
    test_dir = Path(PATHS["tests"])
    
    if not test_dir.exists():
        return False, ["No tests directory found"]
    
    missing = pipe(
        REQUIRED_TESTS,
        toolz_filter(lambda t: not (test_dir / t).exists()),
        toolz_map(lambda t: f"Missing test file: {t}"),
        list
    )
    
    return len(missing) == 0, missing

def check_unused_files() -> Tuple[bool, list]:
    """Check for unused files using functional approach."""
    def extract_imports_ast(file_path: Path) -> set:
        """Extract imports using AST parsing."""
        try:
            tree = ast.parse(read_file_safe(file_path))
            
            # Get all nodes from AST
            all_nodes = list(ast.walk(tree))
            
            # Extract imports from Import nodes
            import_names = pipe(
                all_nodes,
                toolz_filter(lambda n: isinstance(n, ast.Import)),
                toolz_map(lambda n: pipe(n.names, toolz_map(lambda a: a.name), list)),
                concat,
                set
            )
            
            # Extract imports from ImportFrom nodes
            from_imports = pipe(
                all_nodes,
                toolz_filter(lambda n: isinstance(n, ast.ImportFrom) and n.module),
                toolz_map(lambda n: n.module),
                set
            )
            
            return import_names | from_imports
        except:
            return set()
    
    # Get all imports from all files
    all_files = get_python_files(PATHS["source"])
    test_files = get_python_files(PATHS["tests"])
    
    all_imports = pipe(
        all_files + test_files,
        toolz_map(extract_imports_ast),
        lambda sets: reduce(set.union, sets, set()),
        toolz_filter(lambda x: x.startswith("claude_parser")),
        set
    )
    
    # Check each file
    def is_file_used(file_path: Path) -> bool:
        """Check if a file is imported anywhere."""
        if "__init__.py" in str(file_path):
            return True
            
        module_path = str(file_path.relative_to(Path("."))).replace("/", ".").replace("\\", ".").replace(".py", "")
        
        # Check if module or parent is imported
        parts = module_path.split(".")
        module_variants = pipe(
            range(len(parts)),
            toolz_map(lambda i: ".".join(parts[:i+1])),
            list
        )
        
        # Check if any variant is imported
        is_imported = pipe(
            module_variants,
            toolz_map(lambda mv: mv in all_imports),
            any
        )
        
        if is_imported:
            return True
        
        # Check __init__.py re-exports
        parent_init = file_path.parent / "__init__.py"
        if parent_init.exists() and file_path.stem in read_file_safe(parent_init):
            return True
        
        return False
    
    unused = pipe(
        all_files,
        toolz_filter(lambda f: not is_file_used(f)),
        toolz_map(lambda f: f"UNUSED: {f} - Consider removing or integrating"),
        list
    )
    
    return len(unused) == 0, unused

# ==========================================
# Main Verification Runner (SOLID: Interface Segregation)
# ==========================================

def run_all_checks() -> Dict[str, Tuple[bool, list]]:
    """Run all verification checks and return results."""
    return {
        "forbidden_imports": check_forbidden_imports(),
        "approved_libraries": check_approved_libraries(),
        "manual_loops": check_manual_loops(),
        "95_5_principle": check_95_5_principle(),
        "tests_exist": check_tests_exist(),
        "unused_files": check_unused_files(),
    }

def display_results(results: Dict[str, Tuple[bool, list]]) -> int:
    """Display verification results."""
    print(f"\n{COLORS['YELLOW']}═══ 95/5 Principle Compliance Check ═══{COLORS['RESET']}\n")
    
    # Display individual check results
    check_names = {
        "forbidden_imports": "Forbidden imports check",
        "approved_libraries": "Approved libraries only check",
        "manual_loops": f"No manual loops check - {len(results['manual_loops'][1])} violations",
        "95_5_principle": "95/5 principle check",
        "tests_exist": "Test files check",
        "unused_files": f"No unused files check - {len(results['unused_files'][1])} found",
    }
    
    # Process each check result
    def display_check_result(item: tuple) -> None:
        """Display single check result."""
        key, name = item
        passed, violations = results[key]
        print_status(passed, name)
        
        if not passed and violations:
            # Show first 5-10 violations depending on type
            limit = 5 if key in ["approved_libraries", "unused_files"] else 10
            display_violations = violations[:limit]
            
            # Print each violation
            pipe(
                display_violations,
                toolz_map(lambda v: print(f"  {COLORS['RED']}→ {v}{COLORS['RESET']}")),
                list
            )
            
            if len(violations) > limit:
                print(f"  {COLORS['YELLOW']}... and {len(violations) - limit} more{COLORS['RESET']}")
    
    # Display all check results
    pipe(
        check_names.items(),
        toolz_map(display_check_result),
        list
    )
    
    # Calculate totals
    all_passed = pipe(
        results.values(),
        toolz_map(lambda r: r[0]),
        all
    )
    
    total_violations = pipe(
        results.values(),
        toolz_filter(lambda r: not r[0]),
        toolz_map(lambda r: len(r[1])),
        sum
    )
    
    # Display summary
    print(f"\n{COLORS['YELLOW']}═══ Summary ═══{COLORS['RESET']}")
    
    if all_passed:
        print(f"{COLORS['GREEN']}✓ All checks passed! Ready to commit.{COLORS['RESET']}\n")
        return 0
    else:
        print(f"{COLORS['RED']}╔══════════════════════════════════════════════════════════════╗{COLORS['RESET']}")
        print(f"{COLORS['RED']}║  🚫 COMMIT BLOCKED - {total_violations} VIOLATIONS DETECTED 🚫          ║{COLORS['RESET']}")
        print(f"{COLORS['RED']}╚══════════════════════════════════════════════════════════════╝{COLORS['RESET']}\n")
        
        # Breakdown by category
        breakdown = pipe(
            results.items(),
            toolz_filter(lambda x: not x[1][0]),
            toolz_map(lambda x: f"  • {x[0].replace('_', ' ').title()}: {len(x[1][1])}"),
            list
        )
        
        if breakdown:
            print(f"{COLORS['YELLOW']}Violation Breakdown:{COLORS['RESET']}")
            pipe(
                breakdown,
                toolz_map(lambda item: print(f"{COLORS['YELLOW']}{item}{COLORS['RESET']}")),
                list
            )
            print()
        
        print(f"{COLORS['YELLOW']}Fix violations or update verification_config.py{COLORS['RESET']}")
        print(f"After fixing, run: {COLORS['GREEN']}python scripts/verify_spec_v2.py{COLORS['RESET']}\n")
        return 1

def main() -> int:
    """Main entry point."""
    return pipe(
        run_all_checks(),
        display_results
    )

if __name__ == "__main__":
    sys.exit(main())