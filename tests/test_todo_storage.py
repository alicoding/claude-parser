"""Test TodoStorage - Single Responsibility: File I/O."""
import pytest
from pathlib import Path
import orjson
from claude_parser.domain.todo.storage import TodoStorage


def test_get_path():
    """Get correct file path for session/agent."""
    storage = TodoStorage(session_id="abc-123")
    path = storage.get_path()
    assert path.name == "abc-123-agent-abc-123.json"

    # With different agent
    storage = TodoStorage(session_id="abc-123", agent_id="xyz-789")
    path = storage.get_path()
    assert path.name == "abc-123-agent-xyz-789.json"


def test_write_read_roundtrip(tmp_path, monkeypatch):
    """Write and read todos."""
    # Mock home directory
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    storage = TodoStorage(session_id="test-123")
    todos = [{"content": "Test", "status": "pending"}]

    # Write
    path = storage.write(todos)
    assert Path(path).exists()

    # Read back
    read_todos = storage.read()
    assert read_todos == todos


def test_read_nonexistent(tmp_path, monkeypatch):
    """Read returns empty list for missing file."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    storage = TodoStorage(session_id="missing")
    assert storage.read() == []


def test_delete(tmp_path, monkeypatch):
    """Delete todo file."""
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    storage = TodoStorage(session_id="test-delete")
    storage.write([{"content": "Test"}])

    assert storage.delete() == True
    assert storage.delete() == False  # Already deleted
