"""Exit helper functions for Claude Code hooks.

Following 95/5 principle: Each function is ≤ 3 lines of code.
"""

import sys
from typing import NoReturn

import orjson


def exit_success(message: str = "") -> NoReturn:
    """Exit with success code 0 and JSON output."""
    out = {"continue": True, **({} if not message else {"message": message})}
    sys.stdout.buffer.write(orjson.dumps(out))
    sys.exit(0)


def exit_block(reason: str) -> NoReturn:
    """Exit with blocking code 2."""
    print(reason, file=sys.stderr)
    sys.exit(2)


def exit_error(message: str) -> NoReturn:
    """Exit with error code 1."""
    print(message, file=sys.stderr)
    sys.exit(1)
