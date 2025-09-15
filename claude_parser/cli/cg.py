#!/usr/bin/env python3
"""
Git-like CLI for Claude Parser - Main orchestrator
@SINGLE_SOURCE_TRUTH: Delegates to split command modules
@LOC_ENFORCEMENT: <80 LOC by using sub-apps
"""
import typer

app = typer.Typer(help="Git-like interface for Claude Code conversations")

# Import and register all command modules
from . import cg_basic, cg_restore, cg_reset, cg_advanced, cg_reflog

# Add basic commands (status, log)
for command in [cg_basic.status, cg_basic.log]:
    app.command()(command)

# Add restore commands (checkout)
app.command()(cg_restore.checkout)

# Add reset commands (reset, revert)
for command in [cg_reset.reset, cg_reset.revert]:
    app.command()(command)

# Add advanced commands (find, blame)
for command in [cg_advanced.find, cg_advanced.blame]:
    app.command()(command)

# Add reflog commands (reflog, show)
for command in [cg_reflog.reflog, cg_reflog.show]:
    app.command()(command)


if __name__ == "__main__":
    app()