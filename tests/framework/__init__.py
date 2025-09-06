"""
Test framework package - Enforces best practices.

Import this in all tests to get automatic violation prevention.
"""

from .base import (
    EnforcedTestBase,
    TestViolationError,
    assert_interface_contract,
    get_real_claude_transcript,
    mock_framework_dependency,
)

__all__ = [
    'EnforcedTestBase',
    'TestViolationError',
    'assert_interface_contract',
    'get_real_claude_transcript',
    'mock_framework_dependency',
]
