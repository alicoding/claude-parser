"""
Tests for RealClaudeTimeline - Processing authentic Claude Code JSONL.

Uses real Claude Code JSONL data from our test project.
"""

import pytest
from pathlib import Path

from claude_parser.domain.services import RealClaudeTimeline


class TestRealClaudeTimeline:
    """Test RealClaudeTimeline with authentic Claude Code data."""

    @pytest.fixture
    def test_project_path(self):
        """Path to our real Claude Code test project."""
        return Path("/tmp/claude-parser-test-project")

    def test_initialization_with_real_data(self, test_project_path):
        """Should initialize with real Claude Code JSONL files."""
        timeline = RealClaudeTimeline(test_project_path)

        # Should have found tool operations from real JSONL
        assert len(timeline.tool_operations) > 0
        assert len(timeline.raw_events) > 0

        # Should have multiple sessions
        summary = timeline.get_multi_session_summary()
        assert summary['total_sessions'] >= 2
        assert summary['total_operations'] >= 4

        timeline.clear_cache()

    def test_multi_session_detection(self, test_project_path):
        """Should detect multiple Claude Code sessions."""
        timeline = RealClaudeTimeline(test_project_path)

        summary = timeline.get_multi_session_summary()

        # Should have exactly 2 sessions from our test
        assert summary['total_sessions'] == 2
        assert '0c9f3362-4b85-4861-a604-6ef1578e2aa2' in summary['sessions']
        assert '94aeb5b2-3063-496a-9965-9e2dfcd59043' in summary['sessions']

        # Both sessions should have modified hello.py
        for session_data in summary['sessions'].values():
            assert '/private/tmp/claude-parser-test-project/hello.py' in session_data['files_modified']

        timeline.clear_cache()

    def test_uuid_navigation(self, test_project_path):
        """Should navigate by UUID to different file states."""
        timeline = RealClaudeTimeline(test_project_path)

        # Get Edit operations (not Read)
        edit_operations = [op for op in timeline.tool_operations
                          if op.get("tool_name") == "Edit"]

        assert len(edit_operations) >= 2  # Should have Edit operations from both sessions

        # Test checkout by UUID
        first_edit = edit_operations[0]
        uuid = first_edit.get('uuid')
        assert uuid is not None

        state = timeline.checkout_by_uuid(uuid)
        assert state is not None
        assert 'hello.py' in state

        timeline.clear_cache()

    def test_tool_operation_extraction(self, test_project_path):
        """Should correctly extract tool operations from real JSONL structure."""
        timeline = RealClaudeTimeline(test_project_path)

        # Should have Read and Edit operations
        tools_found = set(op.get('tool_name') for op in timeline.tool_operations)
        assert 'Read' in tools_found
        assert 'Edit' in tools_found

        # Each operation should have required fields
        for operation in timeline.tool_operations:
            assert 'uuid' in operation
            assert 'sessionId' in operation
            assert 'timestamp' in operation
            assert 'tool_name' in operation
            assert 'tool_input' in operation

        # Should have file_path for file operations
        file_operations = [op for op in timeline.tool_operations
                          if op.get('tool_name') in ['Read', 'Edit', 'Write', 'MultiEdit']]
        for op in file_operations:
            assert 'file_path' in op

        timeline.clear_cache()

    def test_chronological_ordering(self, test_project_path):
        """Should order operations chronologically across sessions."""
        timeline = RealClaudeTimeline(test_project_path)

        # Operations should be sorted by timestamp
        timestamps = [op.get('timestamp', '') for op in timeline.tool_operations]
        assert timestamps == sorted(timestamps)

        # Should have operations from both sessions interleaved correctly
        session_ids = [op.get('sessionId') for op in timeline.tool_operations]
        unique_sessions = list(set(session_ids))
        assert len(unique_sessions) == 2

        timeline.clear_cache()

    def test_query_operations(self, test_project_path):
        """Should support querying operations with JMESPath."""
        timeline = RealClaudeTimeline(test_project_path)

        # Query for Edit operations
        edit_ops = timeline.query("[?tool_name=='Edit']")
        assert len(edit_ops) >= 2

        for op in edit_ops:
            assert op['tool_name'] == 'Edit'
            assert 'uuid' in op
            assert 'sessionId' in op

        timeline.clear_cache()

    def test_session_isolation(self, test_project_path):
        """Should be able to get operations from specific sessions."""
        timeline = RealClaudeTimeline(test_project_path)

        # Get operations from first session
        first_session_id = timeline.tool_operations[0].get('sessionId')
        session_ops = timeline.get_session_operations(first_session_id)

        assert len(session_ops) >= 2  # Should have Read + Edit from session

        # All operations should be from the same session
        for op in session_ops:
            assert op.get('sessionId') == first_session_id

        timeline.clear_cache()

    def test_handles_permission_errors(self, test_project_path):
        """Should handle real Claude Code permission errors gracefully."""
        timeline = RealClaudeTimeline(test_project_path)

        # Should have processed all operations even with permission errors
        assert len(timeline.tool_operations) > 0

        # Should have created git commits for successful operations
        assert len(timeline._uuid_to_commit) > 0

        timeline.clear_cache()


@pytest.mark.integration
class TestRealClaudeTimelineIntegration:
    """Integration tests with real Claude Code workflow."""

    def test_complete_workflow(self):
        """Test complete workflow: discover -> timeline -> navigate."""
        from claude_parser.discovery import find_all_transcripts_for_cwd

        project_path = Path("/tmp/claude-parser-test-project")

        # Step 1: Discovery should find transcripts
        transcripts = find_all_transcripts_for_cwd(project_path)
        assert len(transcripts) >= 2  # Should find multiple JSONL files

        # Step 2: Timeline should process all transcripts
        timeline = RealClaudeTimeline(project_path)
        assert len(timeline.tool_operations) > 0

        # Step 3: Navigation should work
        summary = timeline.get_multi_session_summary()
        assert summary['total_sessions'] >= 2

        # Step 4: UUID checkout should work
        edit_ops = [op for op in timeline.tool_operations
                   if op.get("tool_name") == "Edit"]
        if edit_ops:
            uuid = edit_ops[0].get('uuid')
            state = timeline.checkout_by_uuid(uuid)
            assert state is not None

        timeline.clear_cache()
