#!/usr/bin/env python3
"""Show todo history - Tinder-style swipe through completed todos."""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo.swiper import TodoSwiper


def main():
    """Show todo history without interaction."""
    # Use discovery to find transcript
    transcript = find_current_transcript()

    if not transcript:
        print("❌ No transcript found for current directory")
        return 1

    print(f"📍 Session: {Path(transcript).stem}")

    # Create swiper from transcript
    swiper = TodoSwiper.from_transcript(transcript)

    if not swiper.history:
        print("📋 No todo history found")
        return 0

    print(f"📱 Found {len(swiper.history)} todo snapshots\n")

    # Show last 3 completed snapshots
    print("🎯 Recent todo completions:")
    for i in range(min(3, len(swiper.history))):
        swiper.current_index = i

        print(f"\n{'─' * 60}")
        swiper.show()

    if len(swiper.history) > 3:
        print(f"\n💡 ... and {len(swiper.history) - 3} more snapshots in history")

    return 0


if __name__ == "__main__":
    sys.exit(main())
