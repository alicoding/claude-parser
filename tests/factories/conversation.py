"""Conversation event factories - eliminates JSONL duplication across tests."""

import factory
from pathlib import Path
import orjson


class ConversationEventFactory(factory.Factory):
    """Base factory for conversation events - eliminates duplicated event creation."""

    class Meta:
        model = dict

    type = "user"
    uuid = factory.Faker("uuid4")
    timestamp = factory.Faker("iso8601")
    cwd = factory.LazyAttribute(lambda obj: "/test/project")


class UserMessageFactory(ConversationEventFactory):
    """Factory for user messages - replaces hardcoded user event dictionaries."""

    type = "user"
    message = factory.SubFactory(
        factory.DictFactory,
        content=factory.Faker("sentence")
    )


class AssistantMessageFactory(ConversationEventFactory):
    """Factory for assistant messages with tool use - eliminates tool_use boilerplate."""

    type = "assistant"
    message = factory.Dict({
        "content": factory.List([
            factory.Dict({
                "type": "tool_use",
                "name": "Write",
                "input": factory.Dict({
                    "file_path": "/test/project/hello.py",
                    "content": "print('Hello World')"
                })
            })
        ])
    })


class EditToolMessageFactory(AssistantMessageFactory):
    """Factory for Edit tool operations."""

    message = factory.Dict({
        "content": factory.List([
            factory.Dict({
                "type": "tool_use",
                "name": "Edit",
                "input": factory.Dict({
                    "file_path": "/test/project/hello.py",
                    "old_string": "print('Hello World')",
                    "new_string": "print('Hello World')\\n\\ndef goodbye():\\n    print('Goodbye')"
                })
            })
        ])
    })


def create_conversation_transcript(events):
    """Helper to create JSONL transcript from event list - eliminates transcript creation duplication."""
    transcript_lines = []
    for event in events:
        transcript_lines.append(orjson.dumps(event).decode())
    return "\\n".join(transcript_lines)
