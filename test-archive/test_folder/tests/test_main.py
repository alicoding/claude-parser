#!/usr/bin/env python3
"""Tests for main module"""

import pytest

def test_main_function():
    from test_folder.main import main
    assert main() == 0