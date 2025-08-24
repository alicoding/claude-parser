#!/usr/bin/env python3
"""
Specification Compliance Verifier
Run this before committing to ensure 95/5 principle is followed
"""
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
import re

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_status(passed: bool, message: str):
    """Print colored status message"""
    symbol = f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"
    print(f"{symbol} {message}")

def check_forbidden_imports() -> Tuple[bool, List[str]]:
    """Check for forbidden imports that violate 95/5 principle"""
    forbidden_patterns = [
        (r"^import json(?:\s|$)", "Use orjson instead of json"),
        (r"^from json import", "Use orjson instead of json"),
        (r"^import requests(?:\s|$)", "Use httpx or ky instead of requests"),
        (r"^import urllib", "Use httpx or ky instead of urllib"),
        (r"^from datetime import", "Use pendulum instead of datetime"),
        (r"^import datetime(?:\s|$)", "Use pendulum instead of datetime"),
        (r"^import threading", "Use asyncio instead of threading"),
        (r"^from threading import", "Use asyncio instead of threading"),
        (r"^import logging(?:\s|$)", "Use loguru instead of logging"),
        (r"^from logging import", "Use loguru instead of logging"),
        (r"^import argparse", "Use click instead of argparse"),
        (r"^import configparser", "Use pydantic-settings instead"),
        (r"^import tqdm", "Use rich.progress instead of tqdm"),
        (r"fetch\(", "Use ky instead of fetch API"),
        (r"axios\.", "Use ky instead of axios"),
    ]
    
    violations = []
    # Only check source files, not node_modules, research files, or generated code
    py_files = [
        f for f in Path(".").rglob("*.py") 
        if not any(part in str(f) for part in ["node_modules", "research", ".pytest_cache", "__pycache__", "verify_spec.py"])
    ]
    ts_files = [
        f for f in list(Path(".").rglob("*.ts")) + list(Path(".").rglob("*.tsx"))
        if not any(part in str(f) for part in ["node_modules", ".next", "dist", "build"])
    ]
    
    for file_path in py_files:
        
        try:
            content = file_path.read_text()
            for line_no, line in enumerate(content.splitlines(), 1):
                for pattern, message in forbidden_patterns:
                    if re.match(pattern, line.strip()):
                        violations.append(
                            f"{file_path}:{line_no} - {message}\n"
                            f"  Found: {line.strip()}"
                        )
        except Exception:
            pass
    
    for file_path in ts_files:
        try:
            content = file_path.read_text()
            for line_no, line in enumerate(content.splitlines(), 1):
                if "fetch(" in line and "// ky:" not in line:
                    violations.append(
                        f"{file_path}:{line_no} - Use ky instead of fetch\n"
                        f"  Found: {line.strip()}"
                    )
                if "axios" in line:
                    violations.append(
                        f"{file_path}:{line_no} - Use ky instead of axios\n"
                        f"  Found: {line.strip()}"
                    )
        except Exception:
            pass
    
    return len(violations) == 0, violations

def check_required_libraries() -> Tuple[bool, List[str]]:
    """Check that required libraries are in dependency files"""
    required_python = [
        "orjson",
        "pydantic",
        "pendulum",
        "loguru",
        "click",
        "rich",
        "httpx",  # or ky-python when available
        "tenacity",
        "watchfiles",
        "tiktoken",
        "pandas",
        "plotly",
    ]
    
    required_typescript = [
        "ky",
        "zod",
        "vitest",
    ]
    
    missing = []
    
    # Check Python dependencies
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        content = pyproject.read_text()
        for lib in required_python:
            if lib not in content:
                missing.append(f"Python: {lib} not in pyproject.toml")
    
    # Check TypeScript dependencies
    package_json = Path("package.json")
    if package_json.exists():
        content = package_json.read_text()
        for lib in required_typescript:
            if lib not in content:
                missing.append(f"TypeScript: {lib} not in package.json")
    
    return len(missing) == 0, missing

def check_95_5_principle() -> Tuple[bool, List[str]]:
    """Check that the 95% use case is actually simple"""
    issues = []
    
    # Check for overly complex APIs
    api_file = Path("claude_parser/__init__.py")
    if api_file.exists():
        content = api_file.read_text()
        
        # The load function should be directly exported (either defined or imported)
        if "def load(" not in content and "load," not in content and "load" not in content:
            issues.append("Missing simple 'load' function in main API")
        
        # Should export the main function in __all__
        if "__all__" in content and "load" not in content:
            issues.append("'load' function not in __all__ exports")
        
        # Check for configuration requirements in basic API
        if "config" in content.lower() and "optional" not in content.lower():
            issues.append("Basic API seems to require configuration")
    
    return len(issues) == 0, issues

def check_models_use_pydantic() -> Tuple[bool, List[str]]:
    """Ensure all models use pydantic.BaseModel"""
    issues = []
    
    model_files = Path(".").rglob("*model*.py")
    for file_path in model_files:
        # Skip test files
        if "test" in str(file_path) or str(file_path).startswith("tests/"):
            continue
        try:
            content = file_path.read_text()
            if "class " in content and "BaseModel" not in content:
                issues.append(f"{file_path} has classes not inheriting from pydantic.BaseModel")
        except Exception:
            pass
    
    return len(issues) == 0, issues

def check_tests_exist() -> Tuple[bool, List[str]]:
    """Check that test files exist for main features"""
    required_tests = [
        "test_parser.py",
        "test_models.py",
        "test_api.py",
    ]
    
    missing = []
    test_dir = Path("tests")
    if test_dir.exists():
        for test_file in required_tests:
            if not (test_dir / test_file).exists():
                missing.append(f"Missing test file: {test_file}")
    else:
        missing.append("No tests directory found")
    
    return len(missing) == 0, missing

def run_verification():
    """Run all verification checks"""
    print(f"\n{YELLOW}═══ 95/5 Principle Compliance Check ═══{RESET}\n")
    
    all_passed = True
    
    # Check forbidden imports
    passed, violations = check_forbidden_imports()
    print_status(passed, f"Forbidden imports check")
    if not passed:
        all_passed = False
        for violation in violations:
            print(f"  {RED}→ {violation}{RESET}")
    
    # Check required libraries
    passed, missing = check_required_libraries()
    print_status(passed, f"Required libraries check")
    if not passed:
        all_passed = False
        for item in missing:
            print(f"  {RED}→ {item}{RESET}")
    
    # Check 95/5 principle
    passed, issues = check_95_5_principle()
    print_status(passed, f"95/5 principle check")
    if not passed:
        all_passed = False
        for issue in issues:
            print(f"  {RED}→ {issue}{RESET}")
    
    # Check pydantic usage
    passed, issues = check_models_use_pydantic()
    print_status(passed, f"Pydantic models check")
    if not passed:
        all_passed = False
        for issue in issues:
            print(f"  {RED}→ {issue}{RESET}")
    
    # Check tests exist
    passed, missing = check_tests_exist()
    print_status(passed, f"Test files check")
    if not passed:
        all_passed = False
        for item in missing:
            print(f"  {YELLOW}→ {item}{RESET}")
    
    print(f"\n{YELLOW}═══ Summary ═══{RESET}")
    if all_passed:
        print(f"{GREEN}✓ All checks passed! Ready to commit.{RESET}\n")
        return 0
    else:
        print(f"{RED}✗ Some checks failed. Fix issues before committing.{RESET}\n")
        print(f"Run {YELLOW}python verify_spec.py{RESET} after fixing to re-check.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_verification())