#!/usr/bin/env python3
"""Test file to verify the hooks work with the SDK."""

import json  # This should trigger the posttool_verify hook
import datetime  # This should also trigger it

def test_function():
    """Function without return type hint."""
    return "test"