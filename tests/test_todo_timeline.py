"""Test TodoTimeline - Integration with Timeline domain."""
import pytest
from pathlib import Path
from claude_parser.domain.todo import TodoManager, TodoTimeline


def test_todo_timeline_from_transcript(tmp_path, monkeypatch):
    """Extract todo timeline from transcript JSONL."""
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    # Create mock transcript with TodoWrite entries
    transcript_path = tmp_path / "test-session.jsonl"
    transcript_content = '''
{"type": "assistant", "timestamp": "2025-01-01T10:00:00Z", "message": {"content": [{"type": "tool_use", "name": "TodoWrite", "input": {"todos": [{"content": "Task 1", "status": "pending", "activeForm": "Working on Task 1"}]}}]}}
{"type": "assistant", "timestamp": "2025-01-01T11:00:00Z", "message": {"content": [{"type": "tool_use", "name": "TodoWrite", "input": {"todos": [{"content": "Task 1", "status": "completed", "activeForm": "Completed Task 1"}]}}]}}
    '''.strip()
    transcript_path.write_text(transcript_content)

    # Extract timeline
    timeline = TodoTimeline.from_transcript(str(transcript_path))

    assert len(timeline.events) == 2
    assert timeline.events[0]["todos"][0]["status"] == "pending"
    assert timeline.events[1]["todos"][0]["status"] == "completed"


def test_todo_timeline_display():
    """Display todo timeline with Rich."""
    events = [
        {
            "timestamp": "2025-01-01T10:00:00Z",
            "todos": [{"content": "Task 1", "status": "pending"}]
        },
        {
            "timestamp": "2025-01-01T11:00:00Z",
            "todos": [{"content": "Task 1", "status": "completed"}]
        }
    ]

    timeline = TodoTimeline(events)
    display = timeline.format_timeline()

    assert "10:00" in display
    assert "☐ Task 1" in display
    assert "11:00" in display
    assert "☒ Task 1" in display


def test_todo_progress_over_time():
    """Track progress percentage over time."""
    events = [
        {
            "timestamp": "2025-01-01T10:00:00Z",
            "todos": [
                {"content": "Task 1", "status": "pending"},
                {"content": "Task 2", "status": "pending"}
            ]
        },
        {
            "timestamp": "2025-01-01T11:00:00Z",
            "todos": [
                {"content": "Task 1", "status": "completed"},
                {"content": "Task 2", "status": "pending"}
            ]
        }
    ]

    timeline = TodoTimeline(events)
    progress = timeline.get_progress_over_time()

    assert progress[0]["percentage"] == 0.0
    assert progress[1]["percentage"] == 50.0
