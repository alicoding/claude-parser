"""
Native LlamaIndex integration using the 95/5 principle.

This is the CORRECT implementation that leverages LlamaIndex's
native capabilities instead of reimplementing everything.
"""

from pathlib import Path
from typing import List, Optional

from claude_parser import load
from claude_parser.discovery import find_project_by_original_path


class NativeProjectExporter:
    """
    Minimal LlamaIndex exporter using native capabilities.

    95/5 Principle: Let LlamaIndex do the heavy lifting.
    """

    def __init__(self, project_path: str):
        """Initialize with project path."""
        self.project_path = Path(project_path)

    def export(self) -> List:
        """
        Export conversations as LlamaIndex-ready documents.

        Returns:
            List of Document objects for LlamaIndex
        """
        # Import here to avoid dependency if not using export
        try:
            from llama_index.core import Document
        except ImportError:
            raise ImportError(
                "llama_index not installed. "
                "Install with: pip install llama-index"
            )

        # Find JSONL files for project
        jsonl_files = self._find_project_jsonl_files()
        if not jsonl_files:
            return []

        documents = []

        # Process each conversation file
        for filepath in jsonl_files:
            # Load with claude_parser
            conv = load(str(filepath))

            # Create simple documents from Q&A pairs
            for i, user_msg in enumerate(conv.user_messages):
                # Find next assistant response
                assistant_msg = None
                for asst in conv.assistant_messages:
                    if asst.parsed_timestamp and user_msg.parsed_timestamp:
                        if asst.parsed_timestamp > user_msg.parsed_timestamp:
                            assistant_msg = asst
                            break

                if assistant_msg:
                    # Create Document with native LlamaIndex class
                    doc = Document(
                        text=f"Q: {user_msg.text_content}\n\nA: {assistant_msg.text_content}",
                        metadata={
                            "project": self.project_path.name,
                            "conversation_id": conv.session_id,
                            "timestamp": assistant_msg.timestamp,
                        }
                    )
                    documents.append(doc)

        return documents

    def _find_project_jsonl_files(self) -> List[Path]:
        """Find JSONL files for this project."""
        claude_projects_dir = Path.home() / ".claude" / "projects"

        # Find by original path
        project_info = find_project_by_original_path(str(self.project_path))

        if project_info:
            encoded_dir = claude_projects_dir / project_info["encoded_name"]
            if encoded_dir.exists():
                return list(encoded_dir.glob("*.jsonl"))

        # Fallback to direct path
        if self.project_path.exists():
            return list(self.project_path.glob("*.jsonl"))

        return []


def export_project(project_path: str):
    """
    One-liner export for LlamaIndex.

    Example:
        documents = export_project("/path/to/project")
        index = VectorStoreIndex.from_documents(documents)
    """
    exporter = NativeProjectExporter(project_path)
    return exporter.export()


# Even simpler if you have llama_index installed
def create_index(project_path: str):
    """
    Create a LlamaIndex directly from project.

    Example:
        index = create_index("/path/to/project")
        results = index.query("What decisions were made?")
    """
    try:
        from llama_index.core import VectorStoreIndex
    except ImportError:
        raise ImportError(
            "llama_index not installed. "
            "Install with: pip install llama-index"
        )

    documents = export_project(project_path)
    return VectorStoreIndex.from_documents(documents)


__all__ = [
    'NativeProjectExporter',
    'export_project',
    'create_index',
]
