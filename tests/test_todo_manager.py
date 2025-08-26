"""Test TodoManager - Integration tests for facade pattern."""
from claude_parser.domain.todo import TodoManager


def test_manager_integration(tmp_path, monkeypatch):
    """Test full workflow through manager."""
    # Mock home directory
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    manager = TodoManager(session_id="test-integration")

    # Parse some todos
    todo_json = """[
        {"content": "Design API", "status": "completed", "activeForm": "Designed API"},
        {"content": "Implement API", "status": "in_progress", "activeForm": "Implementing API"},
        {"content": "Test API", "status": "pending", "activeForm": "Testing API"}
    ]"""

    todos = manager.parse(todo_json)
    assert len(todos) == 3

    # Write and read back
    path = manager.write(todos)
    assert "test-integration-agent-test-integration.json" in path

    read_todos = manager.read()
    assert len(read_todos) == 3

    # Calculate progress
    progress = manager.calculate_progress(read_todos)
    assert progress["completed"] == 1
    assert progress["total"] == 3

    # Cleanup
    assert manager.delete() == True


def test_manager_main_vs_sub_agent(tmp_path, monkeypatch):
    """Test main agent vs sub-agent file naming."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    # Main agent (session_id == agent_id)
    main = TodoManager(session_id="abc-123")
    main.write([{"content": "Main task", "status": "pending"}])

    # Sub-agent (different agent_id)
    sub = TodoManager(session_id="abc-123", agent_id="sub-456")
    sub.write([{"content": "Sub task", "status": "pending"}])

    # Different files created
    main_todos = main.read()
    sub_todos = sub.read()

    assert len(main_todos) == 1
    assert len(sub_todos) == 1
    assert main_todos[0]["content"] == "Main task"
    assert sub_todos[0]["content"] == "Sub task"

    # Cleanup
    main.delete()
    sub.delete()


def test_manager_empty_state(tmp_path, monkeypatch):
    """Test manager with no todos."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    manager = TodoManager(session_id="empty")

    # Read empty
    assert manager.read() == []

    # Progress on empty
    progress = manager.calculate_progress([])
    assert progress["total"] == 0

    # Delete non-existent
    assert manager.delete() == False
