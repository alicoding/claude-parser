# Memory Export API

## Overview

The Memory Export API provides clean data export for semantic search and LlamaIndex integration. It converts Claude conversations into simple dictionaries with `text` and `metadata` fields, ready for indexing.

## Design Philosophy

- **No Business Logic**: Pure data export, no filtering decisions
- **LLM-Ready**: Let LlamaIndex/semantic search handle classification
- **95/5 Principle**: Simple API, libraries do the heavy lifting
- **Generator Pattern**: Memory-efficient for large projects

## API Reference

### MemoryExporter Class

```python
from claude_parser.memory import MemoryExporter

class MemoryExporter:
    """
    Export conversations as memory dictionaries for semantic search.
    
    Follows DDD principles - pure data export with no business logic.
    """
    
    def __init__(self, exclude_tools: bool = False):
        """
        Initialize exporter.
        
        Args:
            exclude_tools: If True, skip tool use/result messages
        """
```

### Core Methods

#### export_as_dicts()

```python
def export_as_dicts(self, conversation: Conversation) -> List[Dict[str, Any]]:
    """
    Export conversation as plain dictionaries for LlamaIndex.
    
    Args:
        conversation: Conversation to export
        
    Returns:
        List of dicts with 'text' and 'metadata' keys
        
    Example:
        exporter = MemoryExporter(exclude_tools=True)
        conv = load("session.jsonl")
        
        dicts = exporter.export_as_dicts(conv)
        # Returns:
        # [
        #     {
        #         "text": "Q: How do I implement OAuth?\nA: OAuth implementation involves...",
        #         "metadata": {
        #             "type": "conversation_pair",
        #             "user_uuid": "msg-001",
        #             "assistant_uuid": "msg-002",
        #             "timestamp": "2024-01-01T00:00:00Z",
        #             "session_id": "abc-123"
        #         }
        #     },
        #     ...
        # ]
        
        # Ready for LlamaIndex
        from llama_index.core import Document
        docs = [Document(text=d["text"], metadata=d["metadata"]) for d in dicts]
    """
```

#### export_project()

```python
def export_project(self, project_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Export all conversations in a project as a generator.
    
    Memory-efficient generator pattern for large projects.
    Automatically discovers all JSONL files in the Claude project.
    
    Args:
        project_path: Path to project (will find Claude directory)
        
    Yields:
        Dictionary with 'text' and 'metadata' for each conversation pair
        
    Example:
        exporter = MemoryExporter(exclude_tools=True)
        
        # Process entire project
        for memory_dict in exporter.export_project("/path/to/myproject"):
            # Each dict is ready for indexing
            semantic_search.index(memory_dict)
            
        # Or collect all at once (careful with memory!)
        all_memories = list(exporter.export_project("/path/to/myproject"))
    """
```

#### export()

```python
def export(self, conversation: Conversation) -> List[ConversationMemory]:
    """
    Export conversation as ConversationMemory objects.
    
    Lower-level method that returns typed objects.
    
    Args:
        conversation: Conversation to export
        
    Returns:
        List of ConversationMemory objects
        
    Example:
        memories = exporter.export(conv)
        for memory in memories:
            print(f"Type: {memory.metadata['type']}")
            print(f"Content: {memory.content[:100]}...")
    """
```

## ConversationMemory Model

```python
from claude_parser.memory import ConversationMemory

@dataclass
class ConversationMemory:
    """
    A memory unit from a conversation.
    
    Designed for semantic search and LlamaIndex compatibility.
    """
    
    content: str  # The actual text content
    metadata: Dict[str, Any]  # Structured metadata
    
    def generate_id(self) -> str:
        """Generate stable ID for this memory."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary."""
```

## Memory Types

The exporter creates different memory types based on content:

| Type | Description | Content Format |
|------|-------------|----------------|
| `conversation_pair` | Q&A pair | `Q: {user}\nA: {assistant}` |
| `tool_use` | Tool interaction | Tool name, input, and result |
| `summary` | Conversation summary | Summary text with metadata |
| `standalone_user` | Unpaired user message | User message content |
| `standalone_assistant` | Unpaired assistant message | Assistant message content |

## Integration Examples

### With LlamaIndex

```python
from llama_index.core import VectorStoreIndex, Document
from claude_parser.memory import MemoryExporter

# Export conversations
exporter = MemoryExporter(exclude_tools=True)
conv = load("conversation.jsonl")
memory_dicts = exporter.export_as_dicts(conv)

# Create LlamaIndex documents
documents = [
    Document(
        text=d["text"],
        metadata=d["metadata"]
    )
    for d in memory_dicts
]

# Build index
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("How did we solve the OAuth problem?")
```

### With Semantic Search Service

```python
from claude_parser.memory import MemoryExporter

class ConversationIndexer:
    """Example integration with semantic-search-service."""
    
    def __init__(self, semantic_search_client):
        self.client = semantic_search_client
        self.exporter = MemoryExporter(exclude_tools=True)
    
    async def index_project(self, project_path: str, collection: str):
        """Index entire project into semantic search."""
        
        for memory_dict in self.exporter.export_project(project_path):
            await self.client.index(
                collection=collection,
                text=memory_dict["text"],
                metadata=memory_dict["metadata"]
            )
    
    async def index_with_checkpoints(self, project_path: str, collection: str):
        """Index with checkpoint support for resume."""
        
        last_id = await self.client.get_checkpoint(collection)
        found_checkpoint = last_id is None
        
        for memory_dict in self.exporter.export_project(project_path):
            memory_id = self._generate_id(memory_dict["metadata"])
            
            if not found_checkpoint:
                if memory_id == last_id:
                    found_checkpoint = True
                continue
            
            await self.client.index(
                collection=collection,
                text=memory_dict["text"],
                metadata=memory_dict["metadata"]
            )
            
            await self.client.save_checkpoint(collection, memory_id)
```

### Streaming Export with Filtering

```python
from claude_parser.memory import MemoryExporter
from claude_parser import load

def export_filtered_memories(project_path: str, start_date: str = None):
    """Export memories with optional filtering."""
    
    exporter = MemoryExporter(exclude_tools=True)
    
    for memory_dict in exporter.export_project(project_path):
        # Client-side filtering (or let LlamaIndex handle it)
        if start_date:
            timestamp = memory_dict["metadata"].get("timestamp")
            if timestamp and timestamp < start_date:
                continue
        
        yield memory_dict

# Usage
for memory in export_filtered_memories("/my/project", start_date="2024-01-01"):
    process(memory)
```

## Performance Characteristics

- **O(n) Export**: Linear time complexity with parent_uuid matching
- **Generator Pattern**: Constant memory usage for project export
- **No Re-parsing**: Leverages existing Conversation objects
- **Efficient Pairing**: 679x faster than timestamp-based matching

## Testing

```python
def test_memory_export():
    """Test memory export functionality."""
    from claude_parser import load
    from claude_parser.memory import MemoryExporter
    
    conv = load("test.jsonl")
    exporter = MemoryExporter(exclude_tools=True)
    
    # Test basic export
    memories = exporter.export_as_dicts(conv)
    assert all("text" in m for m in memories)
    assert all("metadata" in m for m in memories)
    
    # Test metadata structure
    for memory in memories:
        metadata = memory["metadata"]
        assert "type" in metadata
        assert metadata["type"] in [
            "conversation_pair",
            "tool_use",
            "summary",
            "standalone_user",
            "standalone_assistant"
        ]

def test_project_export():
    """Test project-wide export."""
    from claude_parser.memory import MemoryExporter
    
    exporter = MemoryExporter()
    
    # Generator should be memory-efficient
    gen = exporter.export_project("/test/project")
    
    # Process one at a time
    for memory_dict in gen:
        assert "text" in memory_dict
        assert "metadata" in memory_dict
        # Process and discard to maintain low memory
```

## Best Practices

1. **Use Generators for Large Projects**: Don't load everything into memory
2. **Let LLMs Filter**: Export everything, let semantic search decide relevance
3. **Track Export State**: Use metadata IDs for checkpoint/resume
4. **Exclude Tools When Appropriate**: Use `exclude_tools=True` for conversation-focused search
5. **Preserve Metadata**: Pass through all metadata for rich querying

## FAQ

**Q: Why export as dicts instead of LlamaIndex Documents?**
A: Clean separation - we export data, clients choose their document format.

**Q: Should I filter during export?**
A: No - export everything and let LlamaIndex/LLMs handle filtering.

**Q: How do I handle incremental updates?**
A: Use the Watch API with UUID checkpoints, then export new messages.

**Q: Can I customize the text format?**
A: The format is fixed for consistency. Transform after export if needed.

**Q: How do I handle multiple projects?**
A: Export each project to a different collection/index.