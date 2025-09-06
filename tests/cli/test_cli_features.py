"""
CLI Domain: Command-line interface features

Tests 95% use case CLI commands - interface only.
"""

import typer
from claude_parser.cli import app
from ..framework import EnforcedTestBase


class TestCLIFeatures(EnforcedTestBase):
    """Test CLI features - command interface contracts."""

    def test_cli_app_exists(self):
        """Interface: CLI app exists and is Typer instance."""
        assert isinstance(app, typer.Typer)
        assert hasattr(app, 'registered_commands')

    def test_commands_registered(self):
        """Interface: Commands are registered in app."""
        commands = app.registered_commands
        assert len(commands) > 0

        # Check we have some commands registered
        assert isinstance(commands, list)

    def test_cli_help_exists(self):
        """Interface: CLI has help text."""
        assert app.info.help == "Claude Parser - Parse & analyze Claude Code conversations"

    def test_cli_callable(self):
        """Interface: CLI app is callable."""
        assert callable(app)
