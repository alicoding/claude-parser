#!/usr/bin/env python3
"""Debug watch_async functionality."""

import asyncio
from pathlib import Path
from claude_parser.watch import watch_async

async def test_basic_watch():
    """Test basic watch functionality."""
    test_file = Path("debug_test.jsonl")

    # Create test file with proper format
    test_file.write_text('{"type": "user", "uuid": "u1", "sessionId": "test", "message": {"content": "Hello"}}\n')

    print(f"Created test file: {test_file}")

    async def collect_messages():
        """Collect messages from watch_async."""
        count = 0
        async for conv, new_messages in watch_async(test_file):
            print(f"Got {len(new_messages)} new messages")
            for msg in new_messages:
                print(f"  - {msg.type}: {msg.text_content}")
            count += 1
            if count >= 1:  # Stop after first batch
                break

    try:
        # Start watching with timeout
        await asyncio.wait_for(collect_messages(), timeout=5.0)
        print("✅ Watch worked!")
    except asyncio.TimeoutError:
        print("❌ Watch timed out")
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()

if __name__ == "__main__":
    asyncio.run(test_basic_watch())
