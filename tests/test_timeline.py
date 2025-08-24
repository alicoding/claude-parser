"""
Tests for Timeline domain - git-based JSONL navigation.
"""

import pytest
from pathlib import Path
import jsonlines
from claude_parser.timeline import Timeline


class TestTimeline:
    """Test Timeline using GitPython and libraries."""
    
    def test_checkout_latest(self, sample_jsonl_dir):
        """Should checkout latest state."""
        timeline = Timeline(sample_jsonl_dir)
        
        state = timeline.checkout("latest")
        assert 'main.py' in state
        assert state['main.py']['content'] == "print('world')"
        
        timeline.clear_cache()
    
    def test_git_branches(self, sample_jsonl_dir):
        """Should create and list branches."""
        timeline = Timeline(sample_jsonl_dir)
        
        timeline.branch("feature")
        branches = timeline.list_branches()
        assert "feature" in branches
        
        timeline.clear_cache()
    
    def test_query_commits(self, sample_jsonl_dir):
        """Should query commits with jmespath."""
        timeline = Timeline(sample_jsonl_dir)
        
        # Query all commits
        commits = timeline.query("[*]")
        assert len(commits) == 2
        
        # Query with limit
        limited = timeline.query("[*]", limit=1)
        assert len(limited) == 1
        
        timeline.clear_cache()
    
    def test_diff_states(self, sample_jsonl_dir):
        """Should diff using deepdiff."""
        timeline = Timeline(sample_jsonl_dir)
        
        # Create branches at different points
        timeline.branch("v1")
        timeline.branch("v2")
        
        # Diff should work (even if empty for identical states)
        diff = timeline.diff("branch:v1", "branch:v2")
        assert diff is not None
        
        timeline.clear_cache()
    
    def test_handles_multiedit(self, jsonl_with_multiedit):
        """Should handle MultiEdit operations."""
        timeline = Timeline(jsonl_with_multiedit)
        
        state = timeline.checkout("latest")
        assert 'config.py' in state
        assert "PORT = 8080" in state['config.py']['content']
        
        timeline.clear_cache()


@pytest.fixture
def sample_jsonl_dir(tmp_path):
    """Create minimal JSONL for testing."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()
    
    events = [
        {
            "timestamp": "2024-08-23T10:00:00",
            "tool_name": "Write",
            "file_path": "main.py",
            "content": "print('hello')"
        },
        {
            "timestamp": "2024-08-23T11:00:00",
            "tool_name": "Edit",
            "file_path": "main.py",
            "old_string": "hello",
            "new_string": "world"
        }
    ]
    
    with jsonlines.open(jsonl_dir / "test.jsonl", mode='w') as writer:
        writer.write_all(events)
    
    return jsonl_dir


@pytest.fixture
def jsonl_with_multiedit(tmp_path):
    """Create JSONL with MultiEdit operations."""
    jsonl_dir = tmp_path / "jsonl"
    jsonl_dir.mkdir()
    
    events = [
        {
            "timestamp": "2024-08-23T10:00:00",
            "tool_name": "Write",
            "file_path": "config.py",
            "content": ""
        },
        {
            "timestamp": "2024-08-23T11:00:00",
            "tool_name": "MultiEdit",
            "file_path": "config.py",
            "edits": [
                {"old_string": "", "new_string": "DEBUG = True\n"},
                {"old_string": "DEBUG = True\n", "new_string": "DEBUG = True\nPORT = 8080\n"}
            ]
        }
    ]
    
    with jsonlines.open(jsonl_dir / "multi.jsonl", mode='w') as writer:
        writer.write_all(events)
    
    return jsonl_dir