#!/usr/bin/env python3
"""Demo TodoSwiper - Tinder for todos! 📱"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo.swiper import TodoSwiper


def main():
    """Demo todo swiper with current transcript."""
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
    print("\n🎯 Starting at most recent...")

    # Show interactive swiper
    swiper.interactive()

    return 0


if __name__ == "__main__":
    sys.exit(main())
