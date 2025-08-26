#!/usr/bin/env python3
"""Demo TodoManager usage."""
from claude_parser.domain.todo import TodoManager

def main():
    """Demo todo operations."""
    # Client provides session ID explicitly (no guessing)
    session_id = "demo-session-123"
    
    # Create manager
    manager = TodoManager(session_id=session_id)
    
    # Parse some todos (from TodoWrite output)
    todo_json = '''[
        {"content": "Design TodoDomain", "status": "completed", "activeForm": "Designed TodoDomain"},
        {"content": "Write TDD tests", "status": "completed", "activeForm": "Wrote TDD tests"},
        {"content": "Implement with Rich", "status": "in_progress", "activeForm": "Implementing with Rich"},
        {"content": "Create documentation", "status": "pending", "activeForm": "Creating documentation"}
    ]'''
    
    todos = manager.parse(todo_json)
    print(f"Parsed {len(todos)} todos")
    
    # Write to storage
    path = manager.write(todos)
    print(f"Saved to: {path}")
    
    # Display with beautiful tree format
    print("\nTodo Display:")
    manager.display(show_progress=True)
    
    # Read back from storage
    read_todos = manager.read()
    print(f"\nRead {len(read_todos)} todos from storage")
    
    # Show progress
    progress = manager.calculate_progress(read_todos)
    print(f"Progress: {progress['completed']}/{progress['total']} ({progress['percentage']}%)")
    
    # Cleanup
    manager.delete()
    print("\nDemo completed!")

if __name__ == "__main__":
    main()
