#!/usr/bin/env python3
"""Another test to see if hooks work."""

import json  # Violation: should use orjson
import datetime  # Violation: should use pendulum

def bad_code():
    """Function with violations."""
    results = []
    for i in range(10):  # Manual loop violation
        results.append(i * 2)
    return results