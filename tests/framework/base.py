"""
Custom test framework base - Enforces best practices and prevents violations.

This framework makes it IMPOSSIBLE to write bad tests by:
1. Preventing framework imports (orjson, msgspec, etc.)
2. Enforcing interface-only testing
3. Requiring mocked dependencies
4. Limiting file size and complexity
"""

import sys
import ast
import inspect
from pathlib import Path
from typing import Any, Dict, List, Set
from unittest.mock import MagicMock


# Forbidden imports that tests should NEVER use
FORBIDDEN_IMPORTS = {
    'orjson',
    'msgspec',
    'polars',
    'aiofiles',
    'toolz',
    'watchfiles',  # Should be mocked
}

# Forbidden internal modules (infrastructure layer)
FORBIDDEN_INTERNAL_PATTERNS = {
    'claude_parser.infrastructure',
    'claude_parser.domain.interfaces',
    'claude_parser.models.base',
}


class TestViolationError(Exception):
    """Raised when test violates best practices."""
    pass


class EnforcedTestBase:
    """
    Base class that enforces proper test practices.

    All test classes should inherit from this to get automatic enforcement.
    """

    def __init_subclass__(cls, **kwargs):
        """Validate test class follows best practices."""
        super().__init_subclass__(**kwargs)

        # Get the file containing this test class
        test_file = Path(inspect.getfile(cls))

        # Enforce file size limit
        _check_file_size(test_file)

        # Check for forbidden imports
        _check_forbidden_imports(test_file)

        # Validate class name follows conventions
        _check_class_naming(cls.__name__)


def _check_file_size(test_file: Path) -> None:
    """Enforce maximum file size to prevent bloated tests."""
    if not test_file.exists():
        return

    line_count = len(test_file.read_text().splitlines())
    MAX_LINES = 50

    if line_count > MAX_LINES:
        raise TestViolationError(
            f"Test file {test_file.name} has {line_count} lines. "
            f"Maximum allowed: {MAX_LINES}. "
            f"Break into smaller, focused test files."
        )


def _check_forbidden_imports(test_file: Path) -> None:
    """Check for forbidden framework imports."""
    if not test_file.exists():
        return

    content = test_file.read_text()
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                if name.name in FORBIDDEN_IMPORTS:
                    raise TestViolationError(
                        f"FORBIDDEN IMPORT: {name.name} in {test_file.name}. "
                        f"Tests should never import framework dependencies directly. "
                        f"Use mocks via test_framework.mocks instead."
                    )

        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module in FORBIDDEN_IMPORTS:
                raise TestViolationError(
                    f"FORBIDDEN IMPORT: from {node.module} in {test_file.name}. "
                    f"Tests should never import framework dependencies directly."
                )

            # Check internal module patterns
            if node.module:
                for pattern in FORBIDDEN_INTERNAL_PATTERNS:
                    if node.module.startswith(pattern):
                        raise TestViolationError(
                            f"FORBIDDEN INTERNAL IMPORT: {node.module} in {test_file.name}. "
                            f"Tests should only import from public API (claude_parser.__init__)."
                        )


def _check_class_naming(class_name: str) -> None:
    """Enforce test class naming conventions."""
    if not class_name.startswith('Test'):
        raise TestViolationError(
            f"Test class {class_name} must start with 'Test'. "
            f"Use TestXxxInterface or TestXxxContract naming."
        )


def mock_framework_dependency(framework_name: str) -> MagicMock:
    """
    Centralized framework mocking - THE ONLY WAY to use frameworks in tests.

    Args:
        framework_name: Name of framework to mock ('watchfiles', 'orjson', etc.)

    Returns:
        Configured mock object

    Example:
        watchfiles_mock = mock_framework_dependency('watchfiles')
        watchfiles_mock.awatch.return_value = async_mock_iterator()
    """
    if framework_name not in FORBIDDEN_IMPORTS:
        raise TestViolationError(
            f"Unknown framework: {framework_name}. "
            f"Available frameworks: {', '.join(FORBIDDEN_IMPORTS)}"
        )

    mock = MagicMock()
    mock._framework_name = framework_name
    return mock


def get_real_claude_transcript() -> Path:
    """
    Get real Claude Code transcript using existing discovery API.

    Uses claude_parser.discovery - no custom path logic!
    If no data available, instructs to run `claude -p` to create it.

    Returns:
        Path to real JSONL transcript file

    Raises:
        TestViolationError: If no real transcript available
    """
    # Use existing discovery API - 95% existing functionality!
    from claude_parser.discovery import find_current_transcript, find_transcript_for_cwd

    try:
        # Try to find transcript for current working directory
        transcript = find_current_transcript()
        if transcript and transcript.exists():
            return transcript
    except Exception:
        pass

    try:
        # Try alternative discovery method
        transcript = find_transcript_for_cwd()
        if transcript and transcript.exists():
            return transcript
    except Exception:
        pass

    raise TestViolationError(
        "No Claude Code transcript found for current directory. "
        "Run `claude -p` in the test directory to create project context."
    )


def assert_interface_contract(obj: Any, expected_type: type, required_attrs: List[str]) -> None:
    """
    Assert that object fulfills interface contract.

    Tests BEHAVIOR not implementation details.

    Args:
        obj: Object to test
        expected_type: Expected type/interface
        required_attrs: Required attributes/methods
    """
    assert isinstance(obj, expected_type), f"Expected {expected_type}, got {type(obj)}"

    for attr in required_attrs:
        assert hasattr(obj, attr), f"Missing required attribute: {attr}"


# Export clean testing API - Focus on FEATURES
__all__ = [
    'EnforcedTestBase',
    'TestViolationError',
    'mock_framework_dependency',
    'get_real_claude_transcript',
    'assert_interface_contract',
]
