#!/usr/bin/env python3
"""Test clean architecture with real Claude conversation data."""

from claude_parser import load, analyze, ConversationAnalytics

def test_real_data():
    # Use a real JSONL file from the claude-parser project
    real_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser/0db36546-18ed-482e-8b5d-22b58ef80394.jsonl"

    print("Testing clean architecture with real Claude conversation data...")

    try:
        # Test load function
        print("\n1. Testing load() with real data:")
        conversation = load(real_file)
        print(f"Loaded conversation: {len(conversation)} messages")
        print(f"First message type: {conversation[0].get('type', 'unknown')}")

        # Test analyze function
        print("\n2. Testing analyze() with real data:")
        analysis = analyze(real_file)
        print("Analysis results:")
        for key, value in analysis.items():
            print(f"  {key}: {value}")

        # Test ConversationAnalytics
        print("\n3. Testing ConversationAnalytics with real data:")
        analytics = ConversationAnalytics(conversation)
        stats = analytics.get_statistics()
        print("Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✅ ALL TESTS PASSED - Clean architecture works with real data!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_data()
