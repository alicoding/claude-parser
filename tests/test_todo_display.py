"""Test TodoDisplay - Single Responsibility: Formatting."""
import pytest
from rich.tree import Tree
from claude_parser.domain.todo.display import TodoDisplay


def test_build_tree_with_active():
    """Build tree with in-progress task."""
    todos = [
        {"content": "Update Todos", "status": "in_progress", "activeForm": "Updating Todos"},
        {"content": "Design", "status": "completed"},
        {"content": "Implement", "status": "pending"}
    ]
    
    tree = TodoDisplay.build_tree(todos)
    assert isinstance(tree, Tree)
    assert "⏺" in tree.label
    assert "Updating Todos" in tree.label


def test_build_tree_no_active():
    """Build tree with no active task."""
    todos = [
        {"content": "Task 1", "status": "completed"},
        {"content": "Task 2", "status": "pending"}
    ]
    
    tree = TodoDisplay.build_tree(todos)
    assert isinstance(tree, Tree)
    assert "📋" in tree.label


def test_build_tree_empty():
    """Handle empty todos."""
    tree = TodoDisplay.build_tree([])
    assert "No todos" in tree.label


def test_calculate_progress():
    """Calculate progress metrics."""
    todos = [
        {"content": "Done", "status": "completed"},
        {"content": "Doing", "status": "in_progress"},
        {"content": "Todo", "status": "pending"}
    ]
    
    progress = TodoDisplay.calculate_progress(todos)
    assert progress["total"] == 3
    assert progress["completed"] == 1
    assert progress["percentage"] == 33.3


def test_calculate_progress_empty():
    """Handle empty todos in progress."""
    progress = TodoDisplay.calculate_progress([])
    assert progress["total"] == 0
    assert progress["percentage"] == 0