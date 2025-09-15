#!/usr/bin/env python3
"""
Hook Executor Utilities - @UTIL_FIRST design
Reusable utilities for hook execution that can be used by CLI, tests, or other systems
@SINGLE_SOURCE_TRUTH: One place for executor logic
@LOC_ENFORCEMENT: <80 LOC
"""

from typing import Callable, Optional, Tuple, Any, List
from importlib import import_module


def load_executor(executor_name: str) -> Optional[Callable]:
    """Load executor module dynamically - REUSABLE UTILITY

    Can be used by:
    - CLI commands
    - Test suites
    - Other hook systems

    Args:
        executor_name: Module name to import (e.g., 'lnca_plugins')

    Returns:
        Callable that takes HookRequest and returns List[Tuple]
        None if module not found or doesn't have handle_hook
    """
    try:
        module = import_module(executor_name)
        handler = getattr(module, 'handle_hook', None)
        if handler and callable(handler):
            return handler
        return None
    except (ImportError, AttributeError):
        return None


def execute_with_executor(executor_name: str) -> int:
    """Execute hook with named executor - REUSABLE UTILITY

    Complete hook execution pipeline:
    1. Read stdin (delegates to existing util)
    2. Create HookRequest (existing class)
    3. Load executor dynamically
    4. Execute plugins
    5. Aggregate and output results

    Args:
        executor_name: Module name containing handle_hook function

    Returns:
        Exit code (0=success, 2=blocked)
    """
    from .utils import read_stdin, write_output
    from .request import HookRequest

    # @UTIL_FIRST: Use existing read_stdin
    hook_data = read_stdin()

    # @UTIL_FIRST: Use existing HookRequest
    request = HookRequest(hook_data)

    # Load executor using our reusable utility
    executor = load_executor(executor_name)

    if not executor:
        # No executor = pass through (allow)
        write_output(None, 0)
        return 0

    # Execute plugins - executor returns List[Tuple[str, Optional[str]]]
    try:
        results = executor(request)
    except Exception as e:
        # On error, pass through with error message
        write_output(f"Executor error: {e}", 1)
        return 1

    # @UTIL_FIRST: Use HookRequest's complete() method for aggregation
    return request.complete(results)