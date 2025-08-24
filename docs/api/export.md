# Export API - claude-parser

## Overview
Export methods to convert Claude conversations to various formats for integration with memory systems, documentation, and other tools.

## New Methods for Conversation Class

### export_for_mem0() - Memory System Export

```python
def export_for_mem0(
    self,
    include_tools: bool = False,
    include_meta: bool = False,
    include_summaries: bool = False
) -> Dict[str, Any]
```

Exports conversation in mem0-ready format with intelligent filtering.

**Parameters:**
- `include_tools` (bool): Include tool use/results (default: False)
- `include_meta` (bool): Include system meta messages (default: False)
- `include_summaries` (bool): Include summary messages (default: False)

**Returns:**
Dictionary ready for `mem0.add(**result)` with structure:
```python
{
    'messages': [
        {'role': 'user', 'content': 'text'},
        {'role': 'assistant', 'content': 'text'}
    ],
    'user_id': 'session_id',
    'metadata': {
        'source': 'claude_parser',
        'session_id': 'xxx',
        'timestamp': '2024-01-01T12:00:00',
        'conversation_messages': 10,  # After filtering
        'total_messages': 50,          # Before filtering
        'filtered_out': 40             # Removed messages
    }
}
```

**Filtering Logic:**

| Message Type | Default | Reason |
|-------------|---------|--------|
| user | ✅ Include | User input |
| assistant | ✅ Include* | AI response (*text only, tool blocks removed) |
| tool_use | ❌ Filter | File ops, bash commands |
| tool_result | ❌ Filter | Command outputs |
| summary | ❌ Filter | Not conversation |
| meta (isMeta=true) | ❌ Filter | System messages |

**Example Usage:**
```python
from claude_parser import load
from mem0 import Memory

# Load conversation
conv = load("session.jsonl")

# Export only pure conversation (no tools, no meta)
mem0_data = conv.export_for_mem0()

# Add to mem0
if mem0_data:
    mem0 = Memory()
    mem0.add(**mem0_data)
    print(f"Synced {mem0_data['metadata']['conversation_messages']} messages")
```

### Future Export Methods (Planned)

```python
# Export for LangChain
def export_for_langchain(self) -> List[Dict]

# Export as markdown
def export_markdown(self, include_tools: bool = True) -> str

# Export for ChatGPT format
def export_openai_format(self) -> List[Dict]

# Export prompts only
def export_prompts_only(self) -> List[str]

# Export for terminal display
def export_terminal_format(self) -> str
```

## Implementation Details

### Content Cleaning
The `export_for_mem0()` method includes intelligent content cleaning:

1. **Tool Block Removal**: Assistant messages with embedded tool uses have tool blocks stripped
2. **Text Extraction**: Only text content is preserved from complex message structures
3. **Empty Filtering**: Messages with no text content after cleaning are excluded

### Helper Method
```python
def _clean_content_for_mem0(self, msg: Message) -> str:
    """
    Extract only text content, filtering out tool blocks.
    
    For assistant messages with content blocks:
    - Extract only 'text' type blocks
    - Join multiple text blocks with spaces
    - Return empty string if no text content
    """
```

## Integration with mem0-sync

The `export_for_mem0()` method is designed to work seamlessly with mem0-sync:

```python
# In mem0-sync/inputs/jsonl.py
from claude_parser import load

class JSONLInput:
    def get_messages(self, filepath: str, filters: dict):
        conv = load(filepath)
        return conv.export_for_mem0(**filters)
```

## Testing Requirements

1. **Filter Testing**: Verify each message type is filtered correctly
2. **Content Cleaning**: Ensure tool blocks are removed from assistant messages
3. **Empty Handling**: Test with conversations that have no valid messages after filtering
4. **Large Files**: Test streaming for files >100MB
5. **Edge Cases**: 
   - Empty conversations
   - Tool-only sessions
   - Meta-only messages

## File Location

This functionality should be added to:
- `claude_parser/domain/conversation.py` - Main implementation
- `tests/test_export.py` - Comprehensive tests

## Dependencies

No new dependencies required. Uses existing:
- `toolz` for functional filtering
- `pydantic` for validation
- `orjson` for JSON handling