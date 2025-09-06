#!/usr/bin/env python3
"""Demo TodoManager - Show current todos with discovery."""
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo import TodoManager


def main():
    """Demo TodoManager with current session."""
    # Use discovery to find session (no hardcoding)
    transcript = find_current_transcript()

    if not transcript:
        print("❌ No transcript found for current directory")
        return 1

    # Extract session ID from transcript
    session_id = Path(transcript).stem
    print(f"📍 Found session: {session_id}")

    # Create TodoManager for this session
    manager = TodoManager(session_id=session_id)

    # Check if todos exist
    todos = manager.read()
    if not todos:
        print("📋 No active todos (all completed or none set)")
        return 0

    print(f"\n🎯 Found {len(todos)} active todos:")

    # Display using Rich
    manager.display(show_progress=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
