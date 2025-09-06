#!/usr/bin/env python3
"""Show todos from transcript using discovery - zero hardcoding."""
import sys
from pathlib import Path
import orjson

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_parser.discovery.transcript_finder import find_current_transcript
from claude_parser.domain.todo import TodoManager


def extract_todos_from_transcript(transcript_path: str):
    """Extract todos from transcript JSONL file."""
    todos = []

    with open(transcript_path, 'rb') as f:
        for line in f:
            try:
                data = orjson.loads(line)

                # Look for TodoWrite tool usage in message content
                if data.get('type') == 'assistant' and 'message' in data:
                    message = data['message']
                    if 'content' in message:
                        for content_item in message['content']:
                            if (content_item.get('type') == 'tool_use' and
                                content_item.get('name') == 'TodoWrite' and
                                'input' in content_item):

                                todo_input = content_item['input']
                                if 'todos' in todo_input:
                                    todos.extend(todo_input['todos'])

            except (orjson.JSONDecodeError, KeyError):
                continue

    return todos


def main():
    """Show current session's todos from transcript."""
    # Use discovery to find current transcript (no hardcoding)
    transcript = find_current_transcript()

    if not transcript:
        print("❌ No transcript found for current directory")
        print("Make sure you're in a project directory with Claude transcripts")
        return 1

    # Extract session ID from transcript path
    session_id = Path(transcript).stem
    print(f"📍 Found session: {session_id}")
    print(f"📁 Transcript: {transcript}")

    # Extract todos from transcript JSONL
    print("\n🔍 Scanning transcript for TodoWrite calls...")
    todos = extract_todos_from_transcript(transcript)

    if not todos:
        print("📋 No TodoWrite calls found in transcript")
        return 0

    print(f"\n🎯 Found {len(todos)} todos from transcript:")

    # Use TodoManager to display (but don't read from file, use transcript data)
    from claude_parser.domain.todo.display import TodoDisplay
    from rich.console import Console

    # Display using Rich
    tree = TodoDisplay.build_tree(todos)
    console = Console()
    console.print(tree)

    # Show progress
    progress = TodoDisplay.calculate_progress(todos)
    print(f"\nProgress: {progress['completed']}/{progress['total']} ({progress['percentage']}%)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
