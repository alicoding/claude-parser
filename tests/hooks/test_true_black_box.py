#!/usr/bin/env python3
"""
TRUE Black Box Testing - Using REAL data from REAL transcripts
@DOGFOODING: Using our own SDK to test our own SDK
No fixtures, no mocks - just real data!
"""

from claude_parser import load_latest_session
from claude_parser.hooks import HookRequest
from .test_utils import get_real_hook_data_from_current_session


def test_hook_request_with_real_transcript_data():
    """Test HookRequest with REAL hook data from current session"""
    # Get REAL hook events from current session
    real_hook_events = get_real_hook_data_from_current_session()

    if not real_hook_events:
        # No hook events in current session, skip test
        return

    # Test each real hook event
    for hook_data in real_hook_events:
        request = HookRequest(hook_data)

        # Verify hook event name is set
        assert request.hook_event_name, f"No hook_event_name in {hook_data}"

        # If it has transcript_path, verify we can load the conversation
        if request.transcript_path:
            conv = request.conversation
            assert conv is not None, "Should be able to load conversation from transcript_path"
            assert 'messages' in conv, "Conversation should have messages"


def test_hook_request_conversation_access():
    """Test that HookRequest can access its own conversation data"""
    # Get current session
    session = load_latest_session()
    if not session:
        return

    # Find a PostToolUse event (most common)
    for msg in session.get('messages', []):
        if msg.get('hookEventName') == 'PostToolUse' or msg.get('hook_event_name') == 'PostToolUse':
            # Create HookRequest with this real data
            request = HookRequest(msg)

            # The request should be able to access its conversation
            if request.transcript_path:
                conversation = request.conversation
                assert conversation is not None

                # Should be able to get messages
                messages = conversation.get('messages', [])
                assert len(messages) > 0, "Should have messages in conversation"

                # Should be able to filter messages (using our SDK!)
                from claude_parser.navigation import get_latest_assistant_message
                latest = get_latest_assistant_message(messages)
                # May or may not have a latest message, but shouldn't error

            break


def test_complete_with_real_session_context():
    """Test complete() using data from real session"""
    session = load_latest_session()
    if not session:
        return

    # Find any hook event
    for msg in session.get('messages', []):
        if msg.get('hookEventName'):
            request = HookRequest(msg)

            # Test with realistic plugin results
            results = [
                ("allow", "Check passed based on real context"),
                ("allow", None)  # Some plugins don't return messages
            ]

            exit_code = request.complete(results)
            assert exit_code == 0  # Allow = 0

            # Test block scenario
            block_results = [
                ("block", "Violation found in real context")
            ]

            exit_code = request.complete(block_results)
            assert exit_code == 2  # Block = 2

            break