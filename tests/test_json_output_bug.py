"""Test for json_output bug with dict_items."""

import pytest
import orjson
import sys
from io import StringIO
from claude_parser.hooks.json_output import json_output


def test_json_output_with_kwargs(capsys):
    """Test json_output doesn't crash with kwargs."""
    # This should not crash with 'dict_items' object has no attribute 'items'
    with pytest.raises(SystemExit) as exc_info:
        json_output(
            decision="continue",
            hook_type="Stop",
            extra_field="value"
        )
    
    # Should exit successfully
    assert exc_info.value.code == 0
    
    # Should output valid JSON
    captured = capsys.readouterr()
    output = orjson.loads(captured.out)
    assert output["decision"] == "continue"


def test_json_output_stop_event(capsys):
    """Test json_output works for Stop events."""
    with pytest.raises(SystemExit) as exc_info:
        json_output(hook_type="Stop")
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    output = orjson.loads(captured.out)
    assert "decision" in output or "continue" in output