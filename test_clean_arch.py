#!/usr/bin/env python3
"""Test the clean architecture works identically."""

import sys
from pathlib import Path

# Test the new clean API
from claude_parser.api.factory import analyze_conversation, load_conversation

def test_clean_architecture():
    test_file = "/Volumes/AliDev/ai-projects/claude-parser/test_sample.jsonl"

    print("Testing clean architecture API...")

    try:
        # Test analyze_conversation
        print("\n1. Testing analyze_conversation:")
        analysis = analyze_conversation(test_file)
        print(f"Analysis keys: {list(analysis.keys())}")
        print(f"Total messages: {analysis.get('total_messages', 'N/A')}")
        print(f"User messages: {analysis.get('user_messages', 'N/A')}")
        print(f"Assistant messages: {analysis.get('assistant_messages', 'N/A')}")

    except Exception as e:
        print(f"Error in analyze_conversation: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test load_conversation
        print("\n2. Testing load_conversation:")
        conversation = load_conversation(test_file)
        print(f"Conversation loaded: {len(conversation)} messages")
        print(f"First message: {conversation[0] if conversation else 'None'}")

    except Exception as e:
        print(f"Error in load_conversation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_clean_architecture()
