"""Claude Parser SDK - Hooks Domain.

Provides helpers for Claude Code hook scripts.
95% use case: 3 lines to handle any hook.

Example:
    from claude_parser.hooks import hook_input, exit_block, exit_success
    
    data = hook_input()
    if data.tool_name == "Write": exit_block("No writes")
    exit_success()
"""

# Core imports (95% API)
from .input import hook_input
from .models import HookData
from .exits import exit_success, exit_block, exit_error

# Advanced imports (5% API)
from .json_output import json_output, advanced

__all__ = [
    # Core 95% API
    "hook_input",
    "exit_success",
    "exit_block", 
    "exit_error",
    
    # Model
    "HookData",
    
    # Advanced 5% API
    "json_output",
    "advanced",
]

# Version
__version__ = "2.0.0"