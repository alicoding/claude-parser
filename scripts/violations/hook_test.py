#!/usr/bin/env python3
"""Test file to see if hooks are working."""

import json  # Should trigger: use orjson
import datetime  # Should trigger: use pendulum

def test_function():
    """Test function without type hints."""
    data = []
    for i in range(10):  # Manual loop
        data.append(i)
    return data

unused = "not used"  # Should trigger F841