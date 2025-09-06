#!/usr/bin/env python3
"""Test the main public API from __init__.py works identically."""

# Test the clean main API
from claude_parser import (
    load,
    analyze,
    ConversationAnalytics,
    TokenCounter,
    find_current_transcript
)

def test_main_api():
    test_file = "/Volumes/AliDev/ai-projects/claude-parser/test_sample.jsonl"

    print("Testing main public API...")

    try:
        # Test load function
        print("\n1. Testing load():")
        conversation = load(test_file)
        print(f"Loaded conversation: {len(conversation)} messages")
        print(f"First message: {conversation[0]}")

    except Exception as e:
        print(f"Error in load(): {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test analyze function
        print("\n2. Testing analyze():")
        analysis = analyze(test_file)
        print(f"Analysis: {analysis}")

    except Exception as e:
        print(f"Error in analyze(): {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test ConversationAnalytics
        print("\n3. Testing ConversationAnalytics:")
        conversation = load(test_file)
        analytics = ConversationAnalytics(conversation)
        stats = analytics.get_statistics()
        time_analysis = analytics.get_time_analysis()
        tool_analysis = analytics.get_tool_analysis()

        print(f"Statistics: {stats}")
        print(f"Time Analysis: {time_analysis}")
        print(f"Tool Analysis: {tool_analysis}")

    except Exception as e:
        print(f"Error in ConversationAnalytics: {e}")
        import traceback
        traceback.print_exc()

    try:
        # Test TokenCounter
        print("\n4. Testing TokenCounter:")
        counter = TokenCounter()
        count = counter.count_tokens("Hello world!")
        print(f"Token count for 'Hello world!': {count}")

    except Exception as e:
        print(f"Error in TokenCounter: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_api()
