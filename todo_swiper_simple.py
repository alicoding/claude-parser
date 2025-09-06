#!/usr/bin/env python3
"""Simple TodoSwiper demo - just show latest few."""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo.swiper import TodoSwiper


def main():
    """Show last few todo snapshots."""
    # Use discovery to find transcript
    transcript = find_current_transcript()

    if not transcript:
        print("❌ No transcript found for current directory")
        return 1

    print(f"📍 Loading todo history from: {Path(transcript).name}")

    # Create swiper from transcript
    swiper = TodoSwiper.from_transcript(transcript)

    if not swiper.history:
        print("📋 No todo history found in transcript")
        return 0

    print(f"📱 Found {len(swiper.history)} todo snapshots")

    # Show latest 3 snapshots
    for i in range(min(3, len(swiper.history))):
        swiper.current_index = i
        print(f"\n{'='*50}")
        swiper.show()

        if i < min(2, len(swiper.history) - 1):
            input("\nPress Enter for previous snapshot...")

    print(f"\n💡 Use todo_swiper_demo.py for interactive mode!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
