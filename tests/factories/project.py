"""Project setup factories - eliminates tempfile and directory creation duplication."""

import factory
from pathlib import Path
import tempfile
from typing import List

from claude_parser.infrastructure.discovery import MockProjectDiscovery
from .conversation import create_conversation_transcript, UserMessageFactory, AssistantMessageFactory


class ProjectFactory(factory.Factory):
    """Factory for creating test projects - eliminates tempfile directory setup duplication."""

    class Meta:
        model = dict

    project_name = factory.Faker("slug")
    cwd_path = factory.LazyAttribute(lambda obj: f"/test/{obj.project_name}")

    @classmethod
    def create_temp_project(cls, events=None, **kwargs):
        """Create a temporary project with transcript - eliminates 20+ line setup in each test."""
        temp_dir = tempfile.mkdtemp()
        project_path = Path(temp_dir) / "project"
        project_path.mkdir()

        # Create transcript with default or provided events
        if events is None:
            events = [
                UserMessageFactory(cwd=str(project_path)),
                AssistantMessageFactory(cwd=str(project_path))
            ]

        transcript_path = project_path / "session.jsonl"
        transcript_content = create_conversation_transcript(events)
        transcript_path.write_text(transcript_content)

        return {
            "temp_dir": temp_dir,
            "project_path": project_path,
            "transcript_path": transcript_path,
            "events": events
        }

    @classmethod
    def create_mock_discovery(cls, project_data):
        """Create MockProjectDiscovery with project - eliminates mock setup duplication."""
        mock_discovery = MockProjectDiscovery()
        mock_discovery.add_project(
            "test",
            project_data["project_path"],
            [project_data["transcript_path"]]
        )
        return mock_discovery


class TranscriptFactory(factory.Factory):
    """Factory for transcript files - eliminates JSONL file creation duplication."""

    class Meta:
        model = dict

    filename = "session.jsonl"
    events_count = 3

    @classmethod
    def create_with_checkpoints(cls, project_path: Path, **kwargs):
        """Create transcript with user message checkpoints - standard pattern for tests."""
        events = [
            # Initial user message
            UserMessageFactory(
                uuid="user-1",
                timestamp="2025-09-04T10:00:00Z",
                message={"content": "Create a hello world file"},
                cwd=str(project_path)
            ),
            # Assistant creates file
            AssistantMessageFactory(
                uuid="asst-1",
                timestamp="2025-09-04T10:00:01Z",
                cwd=str(project_path)
            ),
            # Second user message (new checkpoint)
            UserMessageFactory(
                uuid="user-2",
                timestamp="2025-09-04T10:05:00Z",
                message={"content": "Add a goodbye function"},
                cwd=str(project_path)
            ),
            # Assistant edits file
            AssistantMessageFactory(
                uuid="asst-2",
                timestamp="2025-09-04T10:05:01Z",
                cwd=str(project_path)
            )
        ]

        transcript_path = project_path / "session.jsonl"
        transcript_content = create_conversation_transcript(events)
        transcript_path.write_text(transcript_content)

        return {
            "transcript_path": transcript_path,
            "events": events
        }
