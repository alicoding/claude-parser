"""TodoDisplay - Single Responsibility: Formatting.

95% library (Rich), 5% glue.
"""
from typing import List, Dict
from rich.tree import Tree


class TodoDisplay:
    """Format todos for display. No I/O, no data manipulation."""

    @staticmethod
    def build_tree(todos: List[Dict]) -> Tree:
        """Build Rich Tree from todos.

        Args:
            todos: List of todo dictionaries

        Returns:
            Rich Tree object for display
        """
        if not todos:
            return Tree("📋 No todos yet")

        # Find active (in_progress) task
        active = next(
            (t for t in todos if t.get("status") == "in_progress"),
            None
        )

        if active:
            # Rich Tree does the formatting (95% library)
            tree = Tree(f"⏺ {active.get('activeForm', active['content'])}")

            # Add other todos as children
            for todo in todos:
                if todo != active:
                    icon = "☒" if todo.get("status") == "completed" else "☐"
                    tree.add(f"{icon} {todo['content']}")
        else:
            # No active task, show as regular list
            tree = Tree("📋 Todo List")
            for todo in todos:
                icon = "☒" if todo.get("status") == "completed" else "☐"
                tree.add(f"{icon} {todo['content']}")

        return tree

    @staticmethod
    def calculate_progress(todos: List[Dict]) -> Dict:
        """Calculate progress metrics.

        Args:
            todos: List of todo dictionaries

        Returns:
            Progress metrics dictionary
        """
        total = len(todos)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "percentage": 0
            }

        # Simple calculation, no manual loops
        completed = sum(1 for t in todos if t.get("status") == "completed")

        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "percentage": round((completed / total * 100), 1)
        }
