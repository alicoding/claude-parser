"""Memory export functionality for Claude Parser.

This module provides functionality for exporting conversation data
to memory systems and vector databases.

Example:
    from claude_parser import load
    from claude_parser.memory import MemoryExporter
    
    conv = load("conversation.jsonl")
    exporter = MemoryExporter()
    
    # Export to memory format
    memories = exporter.export(conv)
    
    # Each memory has content and metadata
    for memory in memories:
        print(f"Memory: {memory.content[:100]}...")
        print(f"ID: {memory.memory_id}")
"""

from .exporter import MemoryExporter, ConversationMemory

__all__ = [
    "MemoryExporter",
    "ConversationMemory",
]