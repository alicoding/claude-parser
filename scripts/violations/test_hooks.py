#!/usr/bin/env python3
"""Test file to trigger the posttool_verify.py hook."""

import json  # Should trigger: use orjson instead
import datetime  # Should trigger: use pendulum instead

def test_function():
    """Test function without type hints."""
    results = []
    for i in range(10):  # Manual loop that should trigger warning
        results.append(i * 2)
    return results

unused_variable = "this will trigger F841"  # Unused variable