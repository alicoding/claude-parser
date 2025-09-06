#!/usr/bin/env python3
"""Test typer help behavior."""

import typer
from typer.testing import CliRunner

app = typer.Typer()

@app.command()
def test_cmd():
    """Test command that should not be called for --help."""
    print("This function was called!")
    return "command executed"

def test_help_behavior():
    """Test if typer calls command function for --help."""
    runner = CliRunner()

    print("Testing --help behavior...")
    result = runner.invoke(app, ["test-cmd", "--help"])
    print(f"Exit code: {result.exit_code}")
    print(f"Output contains 'This function was called!': {'This function was called!' in result.stdout}")
    print(f"First 200 chars: {repr(result.stdout[:200])}")

if __name__ == "__main__":
    test_help_behavior()
