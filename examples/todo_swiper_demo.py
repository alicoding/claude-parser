#!/usr/bin/env python3
"""Demo TodoSwiper - Navigate todo history like Tinder."""
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo import TodoSwiper


def main():
    """Demo todo history navigation."""
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

    print(f"📱 Found {len(swiper.history)} todo snapshots")
    print("\n🎯 Recent completions:")

    # Show last 3 snapshots
    for i in range(min(3, len(swiper.history))):
        swiper.current_index = i
        print(f"\n{'─' * 50}")
        swiper.show()

    if len(swiper.history) > 3:
        print(f"\n💡 ... and {len(swiper.history) - 3} more in history")

    return 0


if __name__ == "__main__":
    sys.exit(main())
