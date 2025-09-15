#!/usr/bin/env python3
"""
ch - Composable Hook CLI
@UTIL_FIRST: Thin wrapper over executor utilities
@FRAMEWORK_FIRST: 100% Typer delegation
@SINGLE_SOURCE_TRUTH: No duplicate logic
"""

import sys
import typer
from typing import Optional

app = typer.Typer(
    name="ch",
    help="Composable hook runner for Claude Code",
    add_completion=False
)


@app.command()
def run(
    executor: Optional[str] = typer.Option(
        None,
        "--executor", "-e",
        envvar="CLAUDE_HOOK_EXECUTOR",
        help="Plugin executor module (e.g., lnca_plugins)"
    )
):
    """Execute hooks with pluggable executors

    Reads hook data from stdin, executes with specified executor,
    and outputs results per Anthropic hook specification.
    """
    if not executor:
        # No executor specified = pass through
        sys.exit(0)

    # @UTIL_FIRST: Use our reusable utility
    # Import only what we need
    from ..hooks.executor import execute_with_executor

    # Execute and exit with the returned code
    exit_code = execute_with_executor(executor)
    sys.exit(exit_code)


if __name__ == "__main__":
    app()