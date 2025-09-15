#!/usr/bin/env python3
"""
Hook Interface Tests: 6 Missing Hook Types - Real Data Pattern
100% framework delegation: Use real hook data extracted from current session
Following existing test_real_hook_data.py pattern
"""
import pytest
from claude_parser import load_latest_session
from claude_parser.hooks.models import HookEvent
from claude_parser.hooks import execute_hook

@pytest.fixture
def real_hook_base():
    """Extract real hook data structure using @API_FIRST_TEST_DATA pattern"""
    session = load_latest_session()
    if not session:
        pytest.skip("No Claude session available")
    
    # Use public API to discover session files - @API_FIRST_TEST_DATA compliant
    from claude_parser import discover_current_project_files
    session_files = discover_current_project_files()
    if not session_files:
        pytest.skip("No session files found via discovery API")
    
    # Use the first available session file 
    transcript_path = str(session_files[0])
    
    return {
        'session_id': session.session_id,
        'transcript_path': transcript_path,
        'cwd': session.metadata.get('cwd', '/tmp'),
    }

class TestAllHookTypesSupported:
    """GREEN: All 9 hook types should be supported by claude-parser"""
    
    def test_all_hook_enum_values_exist(self):
        """GREEN: All hook types should exist in HookEvent enum"""
        assert HookEvent.PRE_TOOL_USE == "PreToolUse"
        assert HookEvent.POST_TOOL_USE == "PostToolUse"
        assert HookEvent.USER_PROMPT_SUBMIT == "UserPromptSubmit"
        assert HookEvent.STOP == "Stop"
        assert HookEvent.SUBAGENT_STOP == "SubagentStop"
        assert HookEvent.NOTIFICATION == "Notification"
        assert HookEvent.PRE_COMPACT == "PreCompact"
        assert HookEvent.SESSION_START == "SessionStart"
        assert HookEvent.SESSION_END == "SessionEnd"

class TestExecuteHookIntegration:
    """GREEN: execute_hook should work with all hook types"""
    
    def test_execute_stop_hook(self):
        """GREEN: execute_hook should handle Stop hooks"""
        # Should not raise exceptions
        execute_hook("Stop", stop_hook_active=True)
    
    def test_execute_subagent_stop_hook(self):
        """GREEN: execute_hook should handle SubagentStop hooks"""
        # Should not raise exceptions
        execute_hook("SubagentStop", stop_hook_active=False)
    
    def test_execute_notification_hook(self):
        """GREEN: execute_hook should handle Notification hooks"""
        # Should not raise exceptions
        execute_hook("Notification", message="Test notification")
    
    def test_execute_pre_compact_hook(self):
        """GREEN: execute_hook should handle PreCompact hooks"""
        # Should not raise exceptions
        execute_hook("PreCompact", trigger="manual", custom_instructions="Focus on performance")
    
    def test_execute_session_start_hook(self):
        """GREEN: execute_hook should handle SessionStart hooks"""
        # Should not raise exceptions
        execute_hook("SessionStart", source="startup")
    
    def test_execute_session_end_hook(self):
        """GREEN: execute_hook should handle SessionEnd hooks"""
        # Should not raise exceptions
        execute_hook("SessionEnd", reason="clear")
        
    def test_existing_hook_types_still_work(self):
        """GREEN: Existing hook types should continue working"""
        execute_hook("PreToolUse", tool_name="Write", tool_input="test content")
        execute_hook("PostToolUse", tool_name="Write", tool_response="success")
        execute_hook("UserPromptSubmit", prompt="test prompt")