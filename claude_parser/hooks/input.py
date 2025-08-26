"""Hook input parsing functionality.

Single Responsibility: Parse JSON from stdin into HookData.
No other logic, no side effects beyond exit on error.
"""

import sys

import orjson
from pydantic import ValidationError

from .models import HookData


def hook_input() -> HookData:
    """Parse hook JSON from stdin.

    Works for ALL 8 Claude Code hook types with zero configuration.
    Single function, single responsibility.

    Returns:
        HookData: Parsed and validated hook data

    Exits:
        1: On invalid JSON or validation errors

    Example:
        data = hook_input()  # That's it!
        print(data.hook_type)
        print(data.tool_name)
    """
    try:
        # Read stdin - Claude Code sends JSON here
        raw_input = sys.stdin.read()

        # Parse JSON using orjson (10x faster than json)
        json_data = orjson.loads(raw_input)

        # Validate and create model using pydantic
        return HookData(**json_data)

    except orjson.JSONDecodeError as e:
        # Invalid JSON format
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    except ValidationError as e:
        # Missing required fields or invalid types
        print(f"Error: Validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        # Catch any other unexpected errors
        print(f"Error: Failed to parse hook input: {e}", file=sys.stderr)
        sys.exit(1)
