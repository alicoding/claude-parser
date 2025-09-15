#!/usr/bin/env python3
"""
Hook Utils - MINIMAL @UTIL_FIRST Implementation
@SINGLE_SOURCE_TRUTH: Only 2 utilities needed for all hook operations
These are INTERNAL utils - public API remains semantic
"""

import sys
import json
from typing import Dict, Any


def read_stdin() -> Dict[str, Any]:
    """Read JSON from stdin - that's it"""
    try:
        return json.loads(sys.stdin.read())
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)


def write_output(data: Any = None, exit_code: int = 0):
    """Write output and exit - handles all cases
    
    Args:
        data: None (no output), str (stderr), dict (JSON stdout)
        exit_code: 0 (success), 1 (error), 2 (block)
    """
    if data is None:
        sys.exit(exit_code)
    elif isinstance(data, str):
        # String goes to stderr for error messages
        print(data, file=sys.stderr)
        sys.exit(exit_code)
    elif isinstance(data, dict):
        # Dict goes to stdout as JSON
        print(json.dumps(data))
        sys.exit(exit_code)
    else:
        # Fallback - convert to string
        print(str(data))
        sys.exit(exit_code)


# That's it! No more functions needed
# Plugins decide what JSON to pass, not us