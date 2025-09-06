#!/usr/bin/env python3
"""
Example: LlamaIndex integration with claude-parser.

This demonstrates the one-liner integration requested in the service request.
"""

from pathlib import Path
from claude_parser.export import ProjectConversationExporter


def main():
    """Demonstrate LlamaIndex export."""

    # Example 1: Export project conversations
    print("=== LlamaIndex Export Example ===\n")

    # Configure export
    config = {
        "exclude_tool_use": True,      # Remove tool noise
        "include_insights": True,       # Include standalone insights
        "include_decisions": True,      # Track decisions
        "include_mistakes": True,       # Learn from mistakes
        "include_learnings": True,      # Capture learnings
    }

    # One-liner export (as requested!)
    project_path = "/path/to/your/project"  # Replace with actual project
    exporter = ProjectConversationExporter(project_path, config)
    documents = exporter.export()

    print(f"Exported {len(documents)} documents ready for LlamaIndex\n")

    # Show sample document structure
    if documents:
        sample = documents[0]
        print("Sample Document:")
        print(f"  Text: {sample.text[:100]}...")
        print(f"  Metadata: {sample.metadata}")
        print()

    # Example 2: Integration with LlamaIndex (if installed)
    try:
        from llama_index.core import VectorStoreIndex, Document as LlamaDoc

        # Convert to LlamaIndex documents
        llama_docs = [
            LlamaDoc(text=doc.text, metadata=doc.metadata)
            for doc in documents
        ]

        # Create index (as requested in success criteria!)
        index = VectorStoreIndex.from_documents(llama_docs)

        # Now we can search project memory
        results = index.query("What architecture decisions were made?")
        print(f"Search Results: {results}")

    except ImportError:
        print("Note: Install llama-index to enable full integration:")
        print("  pip install llama-index")

    # Example 3: Real-time watching
    print("\n=== Real-time Watch Example ===\n")

    from claude_parser.export.llamaindex_exporter import ProjectConversationWatcher

    def on_new_documents(docs):
        """Callback for new documents."""
        print(f"New documents detected: {len(docs)}")
        for doc in docs:
            print(f"  - {doc.metadata['type']}: {doc.text[:50]}...")

        # Here you would update your LlamaIndex
        # index.insert(docs)

    # Set up watcher
    watcher = ProjectConversationWatcher(
        project_path=project_path,
        callback=on_new_documents,
        config=config
    )

    print("Watcher configured (call watcher.start() to begin monitoring)")

    # Example 4: Pattern detection showcase
    print("\n=== Pattern Detection ===\n")

    from claude_parser.export.llamaindex_exporter import PatternDetector

    test_messages = [
        "We decided to use FastAPI for the backend",
        "I learned that async is not always faster",
        "That was wrong, should have used a different approach",
        "Let's pivot to using Django instead",
    ]

    for msg in test_messages:
        msg_type = PatternDetector.classify_message(msg)
        print(f"'{msg[:40]}...' -> Type: {msg_type}")

    print("\n=== Success! ===")
    print("claude-parser now provides LlamaIndex-ready documents with:")
    print("✅ Tool noise filtered out")
    print("✅ Q&A pairs extracted")
    print("✅ Decisions/mistakes/learnings detected")
    print("✅ Project-wide memory aggregation")
    print("✅ Real-time watching capability")
    print("✅ One-liner integration as requested!")


if __name__ == "__main__":
    main()
