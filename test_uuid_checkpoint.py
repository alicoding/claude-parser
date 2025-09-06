#!/usr/bin/env python3
"""Test UUID checkpoint system to verify it works correctly."""

import asyncio
from pathlib import Path

from claude_parser.watch.uuid_tracker import UUIDCheckpointReader
from claude_parser.watch.true_streaming import StreamingJSONLReader


async def test_uuid_checkpoint():
    """Test that UUID checkpointing works correctly."""

    # Use a real test file
    test_file = Path("jsonl-prod-data-for-test/test-data/840f9326-6f99-46d9-88dc-f32fb4754d36.jsonl")

    print("Testing UUID Checkpoint System")
    print("=" * 50)

    # Test 1: Read all messages
    print("\n1. Reading all messages (no checkpoint)...")
    reader = StreamingJSONLReader(test_file)
    all_messages = await reader.get_new_messages()
    print(f"   Total messages: {len(all_messages)}")

    if len(all_messages) > 10:
        # Get UUID from middle of file
        middle_idx = len(all_messages) // 2
        checkpoint_uuid = all_messages[middle_idx]['uuid']
        print(f"   Checkpoint UUID (message {middle_idx}): {checkpoint_uuid}")

        # Test 2: Resume from checkpoint
        print("\n2. Testing resume from checkpoint...")
        reader2 = StreamingJSONLReader(test_file)
        reader2.set_checkpoint(checkpoint_uuid)

        remaining_messages = await reader2.get_new_messages()
        print(f"   Messages after checkpoint: {len(remaining_messages)}")
        print(f"   Expected: {len(all_messages) - middle_idx - 1}")

        # Verify it's correct
        expected_count = len(all_messages) - middle_idx - 1
        if len(remaining_messages) == expected_count:
            print("   ✅ Checkpoint resume works correctly!")
        else:
            print(f"   ❌ Mismatch! Got {len(remaining_messages)}, expected {expected_count}")

        # Test 3: Incremental reading
        print("\n3. Testing incremental reading...")
        reader3 = StreamingJSONLReader(test_file)

        # Read first 5 messages
        first_batch = []
        for msg in all_messages[:5]:
            first_batch.append(msg)
            reader3.processed_uuids.add(msg['uuid'])
            reader3.last_uuid = msg['uuid']

        print(f"   Processed first 5 messages")
        print(f"   Last UUID: {reader3.last_uuid}")

        # Now get "new" messages
        new_messages = await reader3.get_new_messages()
        print(f"   New messages found: {len(new_messages)}")
        print(f"   Expected: {len(all_messages) - 5}")

        if len(new_messages) == len(all_messages) - 5:
            print("   ✅ Incremental reading works!")
        else:
            print(f"   ❌ Mismatch! Got {len(new_messages)}, expected {len(all_messages) - 5}")

        # Test 4: Verify no duplicates
        print("\n4. Testing duplicate prevention...")
        reader4 = StreamingJSONLReader(test_file)

        # Read all
        batch1 = await reader4.get_new_messages()
        # Try to read again (should get nothing)
        batch2 = await reader4.get_new_messages()

        print(f"   First read: {len(batch1)} messages")
        print(f"   Second read: {len(batch2)} messages")

        if len(batch2) == 0:
            print("   ✅ Duplicate prevention works!")
        else:
            print(f"   ❌ Got {len(batch2)} duplicates!")

    print("\n" + "=" * 50)
    print("UUID Checkpoint Testing Complete")


async def test_sync_reader():
    """Test the sync reader UUID implementation."""
    from claude_parser.watch.uuid_tracker import UUIDCheckpointReader

    print("\nTesting Sync UUID Reader")
    print("=" * 50)

    test_file = Path("jsonl-prod-data-for-test/test-data/840f9326-6f99-46d9-88dc-f32fb4754d36.jsonl")

    reader = UUIDCheckpointReader(test_file)
    messages = await reader.get_new_messages()

    print(f"Messages read: {len(messages)}")

    if messages:
        # Test checkpoint
        checkpoint = messages[10]['uuid']
        reader2 = UUIDCheckpointReader(test_file)
        reader2.set_checkpoint(checkpoint)

        remaining = await reader2.get_new_messages()
        print(f"After checkpoint: {len(remaining)} messages")
        print(f"Expected: {len(messages) - 11}")

        if len(remaining) == len(messages) - 11:
            print("✅ Sync reader checkpoint works!")
        else:
            print("❌ Sync reader checkpoint failed!")


if __name__ == "__main__":
    asyncio.run(test_uuid_checkpoint())
    asyncio.run(test_sync_reader())
