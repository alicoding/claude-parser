#!/usr/bin/env python3
"""Debug script to test help command output."""

import sys
from typer.testing import CliRunner
from claude_parser.cg_cli import app

def test_help_commands():
    """Test help commands and print outputs."""
    runner = CliRunner()

    print("=== Testing status --help ===")
    result = runner.invoke(app, ["status", "--help"])
    print(f"Exit code: {result.exit_code}")
    print(f"Stdout length: {len(result.stdout)}")
    # Stderr not captured in CliRunner by default
    print("First 500 chars of stdout:")
    print(repr(result.stdout[:500]))
    print()

    print("=== Testing log --help ===")
    result = runner.invoke(app, ["log", "--help"])
    print(f"Exit code: {result.exit_code}")
    print(f"Stdout length: {len(result.stdout)}")
    print(f"Stderr: {result.stderr}")
    print("First 500 chars of stdout:")
    print(repr(result.stdout[:500]))
    print()

    print("=== Checking assertions ===")
    # Status help checks
    result = runner.invoke(app, ["status", "--help"])
    checks = [
        ("exit_code == 0", result.exit_code == 0),
        ("'Show current project state and session information' in stdout",
         "Show current project state and session information" in result.stdout),
        ("'--sessions' in stdout", "--sessions" in result.stdout)
    ]

    for check_desc, check_result in checks:
        print(f"Status help - {check_desc}: {check_result}")

    # Log help checks
    result = runner.invoke(app, ["log", "--help"])
    checks = [
        ("exit_code == 0", result.exit_code == 0),
        ("'View operation history across all Claude Code sessions' in stdout",
         "View operation history across all Claude Code sessions" in result.stdout),
        ("'--file' in stdout", "--file" in result.stdout),
        ("'--limit' in stdout", "--limit" in result.stdout),
        ("'--sessions' in stdout", "--sessions" in result.stdout)
    ]

    for check_desc, check_result in checks:
        print(f"Log help - {check_desc}: {check_result}")

if __name__ == "__main__":
    test_help_commands()
