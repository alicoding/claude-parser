#!/usr/bin/env python3
"""Test the performance improvement and correctness of parent-uuid matching."""

import time
from claude_parser.memory import MemoryExporter
from claude_parser.application.conversation_service import load
from claude_parser.discovery import find_current_transcript

# Use discovery to find our current project's transcript
test_file = find_current_transcript()
print(f"Testing with: {test_file}")

# Load conversation
conv = load(test_file)
print(f"Loaded {len(conv.messages)} messages")
print(f"  User messages: {len(conv.user_messages)}")
print(f"  Assistant messages: {len(conv.assistant_messages)}")

# Create exporter
exporter = MemoryExporter(exclude_tools=True)

# Test 1: Performance test
print("\n=== Performance Test ===")
start = time.time()
memories = exporter.export(conv)
elapsed = time.time() - start
print(f"Export time: {elapsed:.3f} seconds")
print(f"Memories created: {len(memories)}")
print(f"Time per memory: {elapsed/len(memories)*1000:.2f} ms" if memories else "N/A")

# Test 2: Verify parent-child relationships
print("\n=== Correctness Test ===")
# Sample check - verify the pairing makes sense
if memories:
    sample_memory = memories[0]
    print(f"Sample memory (first):")
    print(f"  Content preview: {sample_memory.content[:100]}...")
    print(f"  Metadata: {sample_memory.metadata}")

    # Check a few more to ensure variety
    print(f"\nChecking first 5 memories have proper Q&A structure:")
    for i, memory in enumerate(memories[:5]):
        has_q = "Q:" in memory.content
        has_a = "A:" in memory.content
        print(f"  Memory {i}: Has Q={has_q}, Has A={has_a}")

# Test 3: Verify parent-uuid matching is working
print("\n=== Parent-UUID Matching Test ===")
# Build our own response map to verify
user_msgs = list(conv.user_messages)
asst_msgs = list(conv.assistant_messages)
response_map = {msg.parent_uuid: msg for msg in asst_msgs if msg.parent_uuid}

# Check how many user messages have responses
matched = sum(1 for u in user_msgs if u.uuid in response_map)
print(f"User messages with responses: {matched}/{len(user_msgs)}")

# Sample verification - check if the pairing makes logical sense
print("\nSample parent-child verification:")
for user_msg in user_msgs[:3]:
    if user_msg.uuid in response_map:
        asst_msg = response_map[user_msg.uuid]
        print(f"User: {user_msg.text_content[:50]}...")
        print(f"  -> Assistant: {asst_msg.text_content[:50]}...")
        print()

# Test 4: Compare with old O(n²) method
print("=== Comparison with Old Method ===")
# Test with smaller subset for old method
test_users = user_msgs[:100]
test_assts = asst_msgs

# Old O(n²) way (using the existing _find_response)
print(f"Testing old O(n²) method with {len(test_users)} users x {len(test_assts)} assistants")
print(f"This would do {len(test_users) * len(test_assts):,} comparisons")

old_matches = 0
start = time.time()
for user_msg in test_users:
    # Simulate old method - linear search
    for asst_msg in test_assts:
        if asst_msg.parsed_timestamp and user_msg.parsed_timestamp:
            if asst_msg.parsed_timestamp > user_msg.parsed_timestamp:
                old_matches += 1
                break
old_time = time.time() - start

# New O(n) way
new_matches = 0
start = time.time()
response_map = {msg.parent_uuid: msg for msg in test_assts if msg.parent_uuid}
for user_msg in test_users:
    if user_msg.uuid in response_map:
        new_matches += 1
new_time = time.time() - start

print(f"\nResults:")
print(f"  Old method: {old_matches} matches in {old_time:.3f}s")
print(f"  New method: {new_matches} matches in {new_time:.3f}s")
print(f"  Speedup: {old_time/new_time:.1f}x faster")

print("\n✅ All tests completed!")
