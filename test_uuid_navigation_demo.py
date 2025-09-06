#!/usr/bin/env python3
"""
UUID Navigation Demo - Complete workflow using discovery service.

This demonstrates the exact workflow you described:
pointA: uuid-456 ("Fix this bug")
fileA #1 (uuid-457) ← step back to here
fileB #1 (uuid-458)
fileA #2 (uuid-459) ← or step back to here
fileA #3 (uuid-460) ← current state
fileC #1 (uuid-461)
"""

import tempfile
from pathlib import Path

import jsonlines
from rich import print
from rich.console import Console
from rich.table import Table

from claude_parser import load
from claude_parser.discovery import find_current_transcript, list_all_projects
from claude_parser.domain.services import Timeline, FileNavigator

console = Console()


def create_demo_conversation():
    """Create a realistic demo conversation with file operations."""
    console.print("🏗️ Creating demo conversation...", style="bold blue")

    # Create temporary directory for our demo
    temp_dir = Path(tempfile.mkdtemp()) / "demo_conversation"
    temp_dir.mkdir()

    # Create realistic conversation with the scenario you described
    events = [
        # User asks to fix bug
        {
            "type": "user",
            "uuid": "uuid-456",
            "sessionId": "demo-session",
            "timestamp": "2024-08-23T10:00:00Z",
            "message": {"content": "Fix this bug in the authentication system"}
        },

        # Point A: Fix starts here
        # fileA #1 - First attempt at fix
        {
            "uuid": "uuid-457",
            "timestamp": "2024-08-23T10:01:00Z",
            "tool_name": "Edit",
            "file_path": "src/auth.py",
            "old_string": "def login(user, password):\n    if user == 'admin':\n        return True",
            "new_string": "def login(user, password):\n    if user == 'admin' and password:\n        return True"
        },

        # fileB #1 - Edit config file
        {
            "uuid": "uuid-458",
            "timestamp": "2024-08-23T10:02:00Z",
            "tool_name": "Write",
            "file_path": "config/auth.json",
            "content": '{"require_password": true, "timeout": 300}'
        },

        # fileA #2 - Second iteration on auth.py
        {
            "uuid": "uuid-459",
            "timestamp": "2024-08-23T10:03:00Z",
            "tool_name": "Edit",
            "file_path": "src/auth.py",
            "old_string": "def login(user, password):\n    if user == 'admin' and password:\n        return True",
            "new_string": "def login(user, password):\n    if user == 'admin' and password and len(password) > 8:\n        return True\n    return False"
        },

        # fileA #3 - Third iteration (current state)
        {
            "uuid": "uuid-460",
            "timestamp": "2024-08-23T10:04:00Z",
            "tool_name": "Edit",
            "file_path": "src/auth.py",
            "old_string": "def login(user, password):\n    if user == 'admin' and password and len(password) > 8:\n        return True\n    return False",
            "new_string": "def login(user, password):\n    # Enhanced security check\n    if user == 'admin' and password and len(password) > 8:\n        return authenticate_user(user, password)\n    return False"
        },

        # fileC #1 - Add helper function
        {
            "uuid": "uuid-461",
            "timestamp": "2024-08-23T10:05:00Z",
            "tool_name": "Write",
            "file_path": "src/auth_helpers.py",
            "content": "def authenticate_user(user, password):\n    # Real authentication logic here\n    return hash(password) == get_stored_hash(user)"
        }
    ]

    # Write to JSONL file
    jsonl_file = temp_dir / "demo.jsonl"
    with jsonlines.open(jsonl_file, mode="w") as writer:
        writer.write_all(events)

    console.print(f"✅ Created demo conversation at: {jsonl_file}", style="green")
    return temp_dir


def demonstrate_discovery_workflow():
    """Demonstrate using discovery service to find and work with transcripts."""
    console.print("\n🔍 Testing Discovery Service...", style="bold yellow")

    # Try to find current transcript (might not exist in this environment)
    current_transcript = find_current_transcript()
    if current_transcript:
        console.print(f"📁 Found current transcript: {current_transcript}", style="green")
        return Path(current_transcript)
    else:
        console.print("📝 No current transcript found, using demo data", style="cyan")
        return None


def demonstrate_uuid_navigation(conversation_dir: Path):
    """Demonstrate the complete UUID navigation workflow."""
    console.print(f"\n🧭 Demonstrating UUID Navigation on: {conversation_dir}", style="bold magenta")

    # Load conversation using claude-parser
    jsonl_file = list(conversation_dir.glob("*.jsonl"))[0]
    conversation = load(str(jsonl_file))

    # Initialize services
    navigator = FileNavigator(conversation.tool_uses)

    console.print(f"\n📊 Conversation loaded: {len(conversation.messages)} messages")
    console.print(f"🔧 Found {len(conversation.tool_uses)} tool operations")

    # Check if this is our demo data or real data
    is_demo_data = any(op.id.startswith("uuid-") for op in conversation.tool_uses[:5] if hasattr(op, 'id'))

    if is_demo_data:
        console.print("🎭 Using demo data - will show planned workflow")
        return demonstrate_demo_workflow(conversation_dir, navigator)
    else:
        console.print("📈 Using real Claude data - will show actual operations")
        return demonstrate_real_workflow(conversation_dir, navigator)


def demonstrate_real_workflow(conversation_dir: Path, navigator: FileNavigator):
    """Demonstrate navigation with real Claude conversation data."""
    console.print("\n🔍 Analyzing Real Claude Conversation...", style="bold cyan")

    # Show summary of what we found
    summary = navigator.get_conversation_file_summary()

    summary_table = Table(title="Real Conversation Analysis")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")

    summary_table.add_row("Total Operations", str(summary['total_operations']))
    summary_table.add_row("Files Modified", str(summary['files_modified']))

    console.print(summary_table)

    # Show files that were modified
    if summary['file_details']:
        files_table = Table(title="Files Modified in This Conversation")
        files_table.add_column("File", style="blue")
        files_table.add_column("Operations", style="green")
        files_table.add_column("First UUID", style="yellow")
        files_table.add_column("Last UUID", style="yellow")

        for file_path, details in list(summary['file_details'].items())[:10]:  # Show first 10
            files_table.add_row(
                file_path,
                str(details['operations_count']),
                details['first_uuid'][:8] + "..." if details['first_uuid'] else "N/A",
                details['last_uuid'][:8] + "..." if details['last_uuid'] else "N/A"
            )

        console.print(files_table)

        # Pick a file with multiple operations to demonstrate navigation
        multi_op_files = {k: v for k, v in summary['file_details'].items()
                         if v['operations_count'] > 1}

        if multi_op_files:
            demo_file = list(multi_op_files.keys())[0]
            console.print(f"\n🎯 Demonstrating navigation on: {demo_file}", style="bold green")

            # Show timeline for this file
            timeline_info = navigator.get_file_navigation_timeline(demo_file)

            nav_table = Table(title=f"Navigation Timeline: {demo_file}")
            nav_table.add_column("Step", style="cyan")
            nav_table.add_column("UUID", style="yellow")
            nav_table.add_column("Operation", style="green")
            nav_table.add_column("Navigate", style="blue")

            for step in timeline_info[:8]:  # Show first 8 steps
                can_nav = "←→" if step['can_undo_to'] or step['can_redo_from'] else "→"
                nav_table.add_row(
                    str(step['step']),
                    step['uuid'][:8] + "...",
                    step['operation'],
                    can_nav
                )

            console.print(nav_table)

            # Show CLI commands for this real file
            jsonl_file = list(conversation_dir.glob("*.jsonl"))[0]
            console.print(f"\n💡 Try these CLI commands on real data:", style="bold cyan")
            console.print(f"python -m claude_parser.cli timeline {jsonl_file} --file '{demo_file}'")
            console.print(f"python -m claude_parser.cli timeline {jsonl_file} --file '{demo_file}' --steps 2")

    return True


def demonstrate_demo_workflow(conversation_dir: Path, navigator: FileNavigator):
    """Demonstrate the planned UUID workflow with demo data."""
    console.print("\n🎭 Demo Data Workflow - The Exact Scenario You Described", style="bold green")

    timeline = Timeline(conversation_dir)

    # Show the file operation scenario
    console.print("\n" + "="*60)
    console.print("🎯 SCENARIO: 'Fix this bug' workflow", style="bold red")
    console.print("="*60)

    # Find the "Fix this bug" starting point
    starting_uuid = "uuid-456"
    console.print(f"📍 Starting point: {starting_uuid} ('Fix this bug')")

    # Show operations after the starting point
    ops_after = navigator.get_operations_after_uuid(starting_uuid)

    table = Table(title="File Operations After 'Fix this bug'")
    table.add_column("Step", style="cyan")
    table.add_column("UUID", style="yellow")
    table.add_column("Operation", style="green")
    table.add_column("File", style="blue")
    table.add_column("Description", style="white")

    descriptions = [
        "fileA #1 - First attempt at fix",
        "fileB #1 - Edit config file",
        "fileA #2 - Second iteration",
        "fileA #3 - Current state (enhanced)",
        "fileC #1 - Add helper function"
    ]

    for i, (op, desc) in enumerate(zip(ops_after, descriptions)):
        file_path = navigator._extract_file_path(op)
        table.add_row(
            str(i + 1),
            op.id[:8] + "...",
            op.name,
            file_path or "N/A",
            desc
        )

    console.print(table)

    # Rest of demo workflow...
    timeline.clear_cache()
    return True


def main():
    """Run the complete UUID navigation demo."""
    console.print("🚀 Claude Parser UUID Navigation Demo", style="bold green")
    console.print("="*50)

    # Step 1: Try discovery service
    real_transcript = demonstrate_discovery_workflow()

    # Step 2: Use demo data (or real if found)
    if real_transcript and real_transcript.exists():
        conversation_dir = real_transcript.parent
        console.print(f"Using real transcript: {real_transcript}")
    else:
        # Create demo conversation
        conversation_dir = create_demo_conversation()

    # Step 3: Demonstrate UUID navigation
    try:
        demonstrate_uuid_navigation(conversation_dir)
        console.print("\n✅ Demo completed successfully!", style="bold green")

        # Show CLI equivalents
        console.print(f"\n💡 Try these CLI commands:", style="bold cyan")
        jsonl_file = list(conversation_dir.glob("*.jsonl"))[0]

        console.print(f"# Show all operations:")
        console.print(f"python -m claude_parser.cli operations {jsonl_file}")

        console.print(f"# Show src/auth.py timeline:")
        console.print(f"python -m claude_parser.cli timeline {jsonl_file} --file src/auth.py")

        console.print(f"# Navigate to step 2:")
        console.print(f"python -m claude_parser.cli timeline {jsonl_file} --file src/auth.py --steps 2")

        console.print(f"# Show diff for uuid-459:")
        console.print(f"python -m claude_parser.cli timeline {jsonl_file} --diff uuid-459")

    except Exception as e:
        console.print(f"❌ Demo failed: {e}", style="bold red")
        return False

    return True


if __name__ == "__main__":
    main()
