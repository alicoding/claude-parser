#!/usr/bin/env python3
"""
Black box test to see filtered conversation format
@TDD_REAL_DATA: Uses real JSONL production data
@LOC_ENFORCEMENT: <80 LOC
"""

import json
from pathlib import Path
from claude_parser import load_session
from claude_parser.filtering import filter_pure_conversation


def test_filter_pure_conversation_format():
    """See what filter_pure_conversation outputs with real data"""

    # Use real JSONL test data
    jsonl_path = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl")
    assert jsonl_path.exists(), f"Test JSONL not found: {jsonl_path}"

    # Load the session
    session = load_session(str(jsonl_path))
    assert session is not None, "Failed to load session"

    # Get messages
    messages = session.get('messages', [])
    print(f"\nTotal messages in session: {len(messages)}")

    # Filter to pure conversation (returns generator, convert to list)
    clean_conversation = list(filter_pure_conversation(messages))
    print(f"Messages after filtering: {len(clean_conversation)}")

    # Show the structure of first few messages
    print("\n=== FILTERED CONVERSATION FORMAT ===\n")
    for i, msg in enumerate(clean_conversation[:5]):  # First 5 messages
        print(f"Message {i+1}:")
        print(f"  Type: {msg.get('type', msg.get('role'))}")

        # Get content in a safe way
        content = msg.get('content', '')
        if isinstance(content, str):
            preview = content[:200] + "..." if len(content) > 200 else content
        else:
            preview = str(content)[:200] + "..."

        print(f"  Content preview: {preview}")
        print(f"  Keys: {list(msg.keys())}")
        print()

    # Test that we have user/assistant messages only
    message_types = set()
    for msg in clean_conversation:
        msg_type = msg.get('type', msg.get('role'))
        message_types.add(msg_type)

    print(f"Message types in filtered conversation: {message_types}")

    # Verify no tool messages
    assert 'tool_use' not in message_types
    assert 'tool_result' not in message_types

    return clean_conversation


if __name__ == "__main__":
    # Run directly to see output
    filtered = test_filter_pure_conversation_format()
    print(f"\n✅ Filter working! Got {len(filtered)} clean messages")