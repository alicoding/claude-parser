#!/usr/bin/env python3
"""Show current todos using discovery and TodoManager - zero hardcoding."""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo import TodoManager


def main():
    """Show current session's todos using discovery."""
    # Use discovery to find current session (no hardcoding)
    transcript = find_current_transcript()

    if not transcript:
        print("❌ No transcript found for current directory")
        print("Make sure you're in a project directory with Claude transcripts")
        return 1

    # Extract session ID from transcript path
    session_id = Path(transcript).stem
    print(f"📍 Found session: {session_id}")
    print(f"📁 Transcript: {transcript}")

    # Create TodoManager for this session
    manager = TodoManager(session_id=session_id)

    # Check if todos exist for current session
    todos = manager.read()
    if not todos:
        print("📋 No todos found for current session")
        print("\n🔍 Checking for any recent todos from this project...")

        # Check all recent todo files to find ones that might be relevant
        todos_dir = Path.home() / ".claude" / "todos"
        if todos_dir.exists():
            # Get all todo files, sorted by modification time
            todo_files = sorted(todos_dir.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)

            # Check first few recent files
            for todo_file in todo_files[:5]:
                test_session_id = todo_file.name.split("-agent-")[0]
                test_manager = TodoManager(session_id=test_session_id)
                test_todos = test_manager.read()

                if test_todos:
                    print(f"\n🎯 Found {len(test_todos)} todos in recent session: {test_session_id}")
                    test_manager.display(show_progress=True)
                    print(f"\n📄 Todo file: {test_manager.storage.get_path()}")
                    return 0

        print("❌ No todos found in any recent sessions")
        return 0

    print(f"\n🎯 Found {len(todos)} todos:")

    # Display using Rich
    manager.display(show_progress=True)

    # Show raw data
    print(f"\n📄 Todo file: {manager.storage.get_path()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
