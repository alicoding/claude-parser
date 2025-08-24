#!/usr/bin/env python3
"""Test file with violations to verify hooks are working."""

import json  # Should trigger: use orjson instead
import datetime  # Should trigger: use pendulum instead
from typing import Any  # Should trigger: avoid Any types

def bad_function(data: Any):  # Any type violation
    """Function with multiple issues."""
    results = []
    for item in data:  # Manual loop - should use toolz
        results.append(item * 2)
    return results

# Unused variable - should trigger F841
unused_var = "this is not used"

def missing_type_hints(x, y):  # Missing type hints
    """Function without type annotations."""
    return x + y