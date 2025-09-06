"""
LlamaIndex-compatible export for project-wide conversation memory.

SOLID: Single Responsibility - LlamaIndex export only
DDD: Uses existing domain services and repositories
95/5: Leverages claude_parser's existing capabilities
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

import pendulum
from toolz import concat
from toolz.curried import filter as toolz_filter
from toolz.curried import map as toolz_map
from toolz.curried import pipe

from ..application.conversation_service import load
from ..discovery import find_project_by_original_path
from ..domain.entities.conversation import Conversation
from ..memory.exporter import MemoryExporter
from ..models import AssistantMessage, UserMessage, Message


@dataclass
class Document:
    """
    LlamaIndex-compatible Document.

    Mimics llama_index.core.Document structure for compatibility.
    """
    text: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "metadata": self.metadata
        }


class PatternDetector:
    """Detects decision patterns in messages."""

    PATTERNS = {
        "decision": [
            r"decided to", r"we should", r"let's go with", r"the plan is",
            r"i'll use", r"i'll implement", r"we'll use", r"best approach is"
        ],
        "mistake": [
            r"that was wrong", r"should have", r"mistake was", r"didn't work",
            r"error was", r"bug was", r"issue is", r"problem was"
        ],
        "learning": [
            r"learned that", r"discovered", r"realized", r"found out",
            r"now i understand", r"turns out", r"interesting that", r"notice that"
        ],
        "pivot": [
            r"changed approach", r"switched to", r"abandoned", r"pivot",
            r"instead of", r"better to", r"actually", r"on second thought"
        ]
    }

    @classmethod
    def classify_message(cls, text: str) -> str:
        """Classify message content by pattern."""
        text_lower = text.lower()

        # Check patterns in priority order
        priority_order = ["pivot", "mistake", "learning", "decision"]

        for category in priority_order:
            patterns = cls.PATTERNS[category]
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return category

        return "qa"  # Default to Q&A


class ProjectConversationExporter:
    """
    Export project-wide conversations for LlamaIndex.

    Handles:
    - Multiple conversation files in a project
    - Tool message filtering
    - Pattern detection for decisions/mistakes/learnings
    - LlamaIndex-compatible Document format
    """

    def __init__(self, project_path: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize exporter.

        Args:
            project_path: Path to Claude project directory
            config: Export configuration
        """
        self.project_path = Path(project_path)
        self.config = config or {}
        self.memory_exporter = MemoryExporter()

    def export(self) -> List[Document]:
        """
        Export all project conversations as LlamaIndex documents.

        Returns:
            List of Document objects ready for LlamaIndex
        """
        # Find all JSONL files in Claude projects directory
        jsonl_files = self._find_project_jsonl_files()

        if not jsonl_files:
            return []

        # Process each file and combine results
        return list(concat(
            self._process_conversation_file(f) for f in jsonl_files
        ))

    def _find_project_jsonl_files(self) -> List[Path]:
        """Find all JSONL files for this project."""
        # Check if project_path is a Claude projects directory
        claude_projects_dir = Path.home() / ".claude" / "projects"

        # Try to find project by original path
        project_info = find_project_by_original_path(str(self.project_path))

        if project_info:
            # Found encoded project directory
            encoded_dir = claude_projects_dir / project_info["encoded_name"]
            if encoded_dir.exists():
                return list(encoded_dir.glob("*.jsonl"))

        # Fallback: Check if project_path itself contains JSONL files
        if self.project_path.exists():
            jsonl_files = list(self.project_path.glob("*.jsonl"))
            if jsonl_files:
                return jsonl_files

        return []

    def _process_conversation_file(self, filepath: Path) -> List[Document]:
        """
        Process a single conversation JSONL file.

        Args:
            filepath: Path to JSONL file

        Returns:
            List of Document objects
        """
        try:
            # Load conversation using claude_parser
            conv = load(str(filepath))

            # Apply filtering based on config
            messages = self._filter_messages(conv)

            # Convert to documents
            return self._create_documents(messages, conv)

        except Exception as e:
            # Log error but continue processing other files
            print(f"Error processing {filepath}: {e}")
            return []

    def _filter_messages(self, conv: Conversation) -> List[Message]:
        """
        Filter messages based on configuration.

        Excludes tool messages if configured.
        """
        if self.config.get("exclude_tool_use", True):
            # Filter out tool-related messages
            return pipe(
                conv.messages,
                toolz_filter(lambda m: self._is_valuable_message(m)),
                list
            )

        return conv.messages

    def _is_valuable_message(self, msg: Message) -> bool:
        """
        Determine if a message contains valuable content.

        Excludes:
        - Tool use/result messages
        - System messages
        - Empty messages
        """
        # Include user and assistant messages
        if not isinstance(msg, (UserMessage, AssistantMessage)):
            return False

        # Check for tool-related content
        text = msg.text_content.lower()

        # Exclude common tool patterns
        tool_indicators = [
            "tool:", "bash:", "read:", "write:", "edit:",
            "grep:", "search:", "ls:", "cat:", "echo:",
            "file created", "file updated", "file deleted",
            "command executed", "running command",
            "file:", "successfully", "created successfully"
        ]

        # Check if this is a tool result message
        if isinstance(msg, UserMessage):
            # User messages with tool results often have these patterns
            if any(indicator in text for indicator in ["file:", "successfully"]):
                return False

        for indicator in tool_indicators:
            if indicator in text:
                return False

        # Must have meaningful content
        return len(text.strip()) > 20

    def _create_documents(
        self,
        messages: List[Message],
        conv: Conversation
    ) -> List[Document]:
        """
        Create LlamaIndex documents from messages.

        Groups Q&A pairs and creates documents with metadata.
        """
        documents = []

        # Process user messages and find responses
        user_messages = [m for m in messages if isinstance(m, UserMessage)]
        assistant_messages = [m for m in messages if isinstance(m, AssistantMessage)]

        for user_msg in user_messages:
            # Find the next assistant response
            assistant_response = self._find_next_assistant_message(
                user_msg,
                assistant_messages
            )

            if assistant_response:
                # Create Q&A document
                doc = self._create_qa_document(
                    user_msg,
                    assistant_response,
                    conv
                )
                documents.append(doc)

        # Also include standalone insights from assistant
        if self.config.get("include_insights", True):
            documents.extend(
                self._extract_standalone_insights(assistant_messages, conv)
            )

        return documents

    def _find_next_assistant_message(
        self,
        user_msg: UserMessage,
        assistant_messages: List[AssistantMessage]
    ) -> Optional[AssistantMessage]:
        """Find the assistant response following a user message."""
        user_time = pendulum.parse(user_msg.timestamp) if user_msg.timestamp else None

        if not user_time:
            return None

        # Find first assistant message after user message
        for asst_msg in assistant_messages:
            if asst_msg.timestamp:
                asst_time = pendulum.parse(asst_msg.timestamp)
                if asst_time > user_time:
                    return asst_msg

        return None

    def _create_qa_document(
        self,
        user_msg: UserMessage,
        assistant_msg: AssistantMessage,
        conv: Conversation
    ) -> Document:
        """Create a Q&A document from message pair."""
        # Combine Q&A for context
        text = f"Q: {user_msg.text_content}\n\nA: {assistant_msg.text_content}"

        # Detect content type
        content_type = PatternDetector.classify_message(
            user_msg.text_content + " " + assistant_msg.text_content
        )

        # Build metadata
        metadata = {
            "timestamp": assistant_msg.timestamp,
            "conversation_id": conv.session_id,
            "type": content_type,
            "project": self.project_path.name,
            "user_uuid": user_msg.uuid,
            "assistant_uuid": assistant_msg.uuid,
        }

        # Add git branch if available
        if conv.git_branch:
            metadata["branch_id"] = conv.git_branch

        # Add token count if available
        if hasattr(assistant_msg, "total_tokens"):
            metadata["tokens"] = assistant_msg.total_tokens

        return Document(text=text, metadata=metadata)

    def _extract_standalone_insights(
        self,
        assistant_messages: List[AssistantMessage],
        conv: Conversation
    ) -> List[Document]:
        """
        Extract standalone insights from assistant messages.

        Looks for important insights that aren't direct Q&A responses.
        """
        insights = []

        for msg in assistant_messages:
            text = msg.text_content

            # Check if this contains an insight pattern
            content_type = PatternDetector.classify_message(text)

            if content_type in ["decision", "learning", "pivot", "mistake"]:
                # This is a valuable insight
                doc = Document(
                    text=text,
                    metadata={
                        "timestamp": msg.timestamp,
                        "conversation_id": conv.session_id,
                        "type": f"insight_{content_type}",
                        "project": self.project_path.name,
                        "assistant_uuid": msg.uuid,
                    }
                )
                insights.append(doc)

        return insights


class ProjectConversationWatcher:
    """
    Watch for new conversations and auto-export to LlamaIndex.

    Uses claude_parser's watch capabilities for real-time updates.
    """

    def __init__(
        self,
        project_path: str,
        callback: callable,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize watcher.

        Args:
            project_path: Path to Claude project
            callback: Function to call with new documents
            config: Export configuration
        """
        self.exporter = ProjectConversationExporter(project_path, config)
        self.callback = callback
        self.processed_messages = set()

    def start(self):
        """Start watching for new conversations."""
        from ..watch import watch

        # Find JSONL files to watch
        jsonl_files = self.exporter._find_project_jsonl_files()

        for filepath in jsonl_files:
            # Watch each file for updates
            watch(
                str(filepath),
                callback=self._on_new_messages
            )

    def _on_new_messages(self, conv: Conversation, new_messages: List[Message]):
        """Handle new messages from watch."""
        # Filter to valuable messages
        valuable = [
            msg for msg in new_messages
            if self.exporter._is_valuable_message(msg)
        ]

        if not valuable:
            return

        # Create documents for new messages
        documents = self.exporter._create_documents(valuable, conv)

        # Call callback with new documents
        if documents:
            self.callback(documents)


# Export for convenience
__all__ = [
    'Document',
    'ProjectConversationExporter',
    'ProjectConversationWatcher',
    'PatternDetector',
]
