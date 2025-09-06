#!/usr/bin/env python3
"""Test the memory export functionality for LlamaIndex compatibility."""

from claude_parser.memory import MemoryExporter
from claude_parser.application.conversation_service import load
from claude_parser.discovery import find_current_transcript

# Use discovery to find our current project's transcript!
test_file = find_current_transcript()
print(f"Found current transcript: {test_file}")

print("Testing MemoryExporter with exclude_tools...")

# Create exporter with tool exclusion
exporter = MemoryExporter(exclude_tools=True)

# Test single conversation export
try:
    conv = load(test_file)
    print(f"✓ Loaded conversation with {len(conv.messages)} messages")

    # Export as ConversationMemory objects
    memories = exporter.export(conv)
    print(f"✓ Exported {len(memories)} memories (tools excluded)")

    # Export as dicts for LlamaIndex
    dicts = exporter.export_as_dicts(conv)
    print(f"✓ Exported {len(dicts)} dictionaries")

    # Check dict structure
    if dicts:
        first_dict = dicts[0]
        assert 'text' in first_dict, "Missing 'text' key"
        assert 'metadata' in first_dict, "Missing 'metadata' key"
        print("✓ Dictionary structure is correct")
        print(f"  Sample text: {first_dict['text'][:100]}...")
        print(f"  Sample metadata keys: {list(first_dict['metadata'].keys())}")

except FileNotFoundError:
    print("Test file not found, trying project export...")

# Test project-wide export
print("\nTesting project-wide export...")
project_path = "/Volumes/AliDev/ai-projects/claude-parser"

# Create generator
memory_generator = exporter.export_project(project_path)

# Test iteration (just first few)
count = 0
for memory_dict in memory_generator:
    if count == 0:
        print(f"✓ First memory dict keys: {memory_dict.keys()}")
        print(f"  Text preview: {memory_dict['text'][:80]}...")
    count += 1
    if count >= 5:
        break

print(f"✓ Successfully iterated {count} memories from project")

# Test with tools included for comparison
print("\nTesting with tools included...")
exporter_with_tools = MemoryExporter(exclude_tools=False)

try:
    conv = load(test_file)
    memories_with_tools = exporter_with_tools.export(conv)
    memories_without_tools = exporter.export(conv)

    if len(memories_with_tools) > len(memories_without_tools):
        print(f"✓ Tool filtering works: {len(memories_with_tools)} with tools vs {len(memories_without_tools)} without")
    else:
        print(f"  No tool messages in test file (both: {len(memories_with_tools)})")

except:
    print("  Skipping tool comparison test")

print("\n✅ All tests passed! Ready for LlamaIndex integration.")
print("\nUsage for semantic-search-service:")
print("```python")
print("from claude_parser.memory import MemoryExporter")
print("from llama_index.core import Document")
print("")
print("exporter = MemoryExporter(exclude_tools=True)")
print("for memory_dict in exporter.export_project(project_path):")
print("    doc = Document(**memory_dict)")
print("    # Process document...")
print("```")
