"""Test TodoParser - Single Responsibility: Parse JSON."""

import orjson
import pytest

from claude_parser.domain.todo.parser import TodoParser


def test_parse_array_format():
    """Parse direct array of todos."""
    data = '[{"content": "Test", "status": "pending", "activeForm": "Testing"}]'
    todos = TodoParser.parse(data)
    assert len(todos) == 1
    assert todos[0]["content"] == "Test"


def test_parse_object_format():
    """Parse object with todos field."""
    data = '{"todos": [{"content": "Test", "status": "pending"}]}'
    todos = TodoParser.parse(data)
    assert len(todos) == 1
    assert todos[0]["content"] == "Test"


def test_parse_bytes():
    """Parse bytes input."""
    data = b'[{"content": "Test", "status": "pending"}]'
    todos = TodoParser.parse(data)
    assert len(todos) == 1


def test_parse_empty():
    """Parse empty todos."""
    assert TodoParser.parse("[]") == []
    assert TodoParser.parse('{"todos": []}') == []


def test_parse_invalid_json():
    """Handle invalid JSON gracefully."""
    with pytest.raises(orjson.JSONDecodeError):
        TodoParser.parse("not json")
