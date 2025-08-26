"""
Demonstration of using test factory to eliminate duplication.

BEFORE: 4 duplicated tests with 20+ lines each (80+ lines total)
AFTER: 4 one-line tests using factory (8 lines total)
REDUCTION: 90% less code
"""

import pytest
from tests.test_factories import HookTestFactory, TOOL_OUTPUTS


class TestToolResponsesUsingFactory:
    """Tests using factory pattern - 90% less duplication."""
    
    def test_ls_response(self):
        """Test LS tool response."""
        test = HookTestFactory.create_tool_response_test('LS', TOOL_OUTPUTS['LS'])
        test()
    
    def test_grep_response(self):
        """Test Grep tool response."""
        test = HookTestFactory.create_tool_response_test('Grep', TOOL_OUTPUTS['Grep'])
        test()
    
    def test_read_response(self):
        """Test Read tool response."""
        test = HookTestFactory.create_tool_response_test('Read', TOOL_OUTPUTS['Read'])
        test()
    
    def test_bash_response(self):
        """Test Bash tool response."""
        test = HookTestFactory.create_tool_response_test('Bash', TOOL_OUTPUTS['Bash'])
        test()


# Even better: Parameterized version (4 lines total!)
@pytest.mark.parametrize("tool_name,output", [
    ('LS', TOOL_OUTPUTS['LS']),
    ('Grep', TOOL_OUTPUTS['Grep']),
    ('Read', TOOL_OUTPUTS['Read']),
    ('Bash', TOOL_OUTPUTS['Bash']),
])
def test_all_tool_responses_parametrized(tool_name, output):
    """Single parameterized test replaces 4 duplicated tests."""
    test = HookTestFactory.create_tool_response_test(tool_name, output)
    test()