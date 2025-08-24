# Claude Parser SDK - Delivery Contract & Scope Lock

## AGREEMENT
This document represents the COMPLETE scope. Nothing else will be added without explicit discussion.

## What We ARE Building

### Core Product: Claude Code JSONL Parser SDK
A specialized parser for Claude Code conversation files (.jsonl) that enables:
1. **Memory Integration** - Export to mem0 for context persistence
2. **Event Monitoring** - Real-time file watching for new messages
3. **Message Extraction** - Query messages by type, time, content
4. **Session Analysis** - Understand conversation flow and relationships

### What We are NOT Building
- ❌ Generic JSONL parser (only Claude Code format)
- ❌ Claude Code UI replacement
- ❌ Vector database implementation (use existing)
- ❌ Custom embedding models (use existing)
- ❌ Authentication system
- ❌ Cloud deployment
- ❌ REST API server (library only)
- ❌ Custom visualization tools (export only)

## Phased Delivery Plan

### PHASE 1: Foundation (Week 1)
**Deliverables:**
1. **Core Parser** - Parse Claude Code JSONL format
2. **Message Models** - Typed representations of all message types
3. **Basic API** - One-line interface for 95% use cases

**Success Criteria:**
```python
# This MUST work
from claude_parser import load
conv = load("session.jsonl")
print(conv.messages)  # Returns all messages
print(conv.session_id)  # Returns session ID
```

**NOT in Phase 1:**
- No streaming (full file load only)
- No async support
- No error recovery
- No filtering

### PHASE 2: Query Capabilities (Week 2)
**Deliverables:**
1. **Message Filtering** - By type (user/assistant/tool)
2. **Time Navigation** - Before/after/between timestamps
3. **Content Search** - Find messages containing text
4. **Tool Extraction** - Get all tool uses

**Success Criteria:**
```python
conv.assistant_messages  # Just assistant msgs
conv.tool_uses           # All tool interactions
conv.before_summary(20)  # Last 20 before summary
conv.with_errors()       # Messages with errors
```

**NOT in Phase 2:**
- No regex search
- No semantic search
- No complex queries
- No SQL-like interface

### PHASE 3: Memory Export (Week 3)
**Deliverables:**
1. **mem0 Integration** - Direct export to mem0
2. **Metadata Preservation** - Keep session, timestamp, type
3. **Batch Operations** - Efficient bulk export
4. **Simple Embeddings** - Basic text vectors

**Success Criteria:**
```python
conv.to_mem0()  # Exports to mem0
memories = conv.extract_memories()  # Get memory format
```

**NOT in Phase 3:**
- No custom embedding models
- No vector database setup
- No memory retrieval (export only)
- No memory management

### PHASE 4: Real-time Monitoring (Week 4)
**Deliverables:**
1. **File Watching** - Monitor JSONL for changes
2. **Event Emission** - Trigger on new messages
3. **Incremental Parsing** - Only parse new lines
4. **Basic Callbacks** - Register handlers

**Success Criteria:**
```python
from claude_parser import watch

for message in watch("active.jsonl"):
    print(f"New: {message.type}")
```

**NOT in Phase 4:**
- No distributed events
- No webhook support
- No queue integration
- No complex event routing

### PHASE 5: TypeScript Port (Week 5)
**Deliverables:**
1. **Core Parser** - Same as Python Phase 1
2. **Type Definitions** - Full TypeScript types
3. **Streaming Support** - Async iterators
4. **NPM Package** - Publishable module

**Success Criteria:**
```typescript
import { load } from 'claude-parser';
const conv = await load('session.jsonl');
console.log(conv.messages);
```

**NOT in Phase 5:**
- No React components
- No UI elements
- No browser support (Node only)
- No visualization

## Feature Scope (LOCKED)

### Message Types Supported
✅ User messages
✅ Assistant messages
✅ Tool use (Edit, Read, etc.)
✅ Tool results
✅ Summaries
✅ System messages

### Operations Supported
✅ Load full file
✅ Filter by type
✅ Search by content
✅ Navigate by time
✅ Export to mem0
✅ Watch for changes

### Operations NOT Supported
❌ Modify JSONL files
❌ Create new conversations
❌ Merge conversations
❌ Split conversations
❌ Replay conversations
❌ Simulate conversations

## Technical Boundaries

### Performance Targets
- Parse 10MB file: < 1 second
- Memory usage: < 2x file size
- Watch latency: < 100ms
- Export speed: 1000 msgs/second

### Limits
- Max file size: 1GB
- Max messages: 1 million
- Max watchers: 10 concurrent
- Max export batch: 1000 items

## API Surface (FINAL)

### Python API
```python
# Loading
conv = load(path: str) -> Conversation
conv = load_many(paths: List[str]) -> List[Conversation]

# Properties (read-only)
conv.messages -> List[Message]
conv.session_id -> str
conv.assistant_messages -> Iterator[Message]
conv.user_messages -> Iterator[Message]
conv.tool_uses -> Iterator[ToolUse]

# Methods
conv.filter(predicate) -> Iterator[Message]
conv.search(text: str) -> Iterator[Message]
conv.at(timestamp) -> Optional[Message]
conv.between(start, end) -> Iterator[Message]
conv.before_summary(n: int) -> List[Message]

# Export
conv.to_mem0() -> Dict
conv.to_dict() -> Dict
conv.to_jsonl() -> str

# Monitoring
watch(path: str) -> Iterator[Message]
watch_many(paths: List[str]) -> Iterator[Tuple[str, Message]]
```

### TypeScript API
```typescript
// Same as Python but with types
interface Conversation {
  messages: Message[];
  sessionId: string;
  assistantMessages: Message[];
  // ... etc
}
```

## What Success Looks Like

### For Users
1. **One line to load** - No configuration needed
2. **Intuitive queries** - Natural property access
3. **Fast performance** - No waiting
4. **mem0 ready** - Direct integration
5. **Real-time capable** - Watch mode works

### For Developers
1. **Clean codebase** - Ready for GitHub
2. **Well tested** - 95% coverage
3. **Documented** - Every function
4. **Type safe** - Full typing
5. **No dependencies hell** - Minimal deps

## Out of Scope (NEVER)

These will NEVER be added:
1. **Database storage** - Use existing DBs
2. **Web server** - Library only
3. **Authentication** - User's responsibility  
4. **Cloud sync** - Local only
5. **GUI/TUI** - Programmatic only
6. **Analytics dashboard** - Export only
7. **LLM integration** - Parse only
8. **Custom formats** - Claude Code only

## Change Management

### To Add ANYTHING to this scope:
1. Must be discussed explicitly
2. Must have clear value
3. Must not break 95/5 principle
4. Must not delay delivery
5. Must be documented here

### Current Scope Status
- **Locked**: ✅
- **Changes**: 0
- **Scope creep**: BLOCKED

## Delivery Timeline

| Week | Phase | Deliverable | Status |
|------|-------|------------|---------|
| 1 | Phase 1 | Core Parser + Models + API | ⏳ |
| 2 | Phase 2 | Query Capabilities | ⏳ |
| 3 | Phase 3 | Memory Export | ⏳ |
| 4 | Phase 4 | Real-time Monitoring | ⏳ |
| 5 | Phase 5 | TypeScript Port | ⏳ |

## Sign-off

This document represents the COMPLETE scope of the Claude Parser SDK project.

**Agreed Scope:**
- 5 phases
- 5 weeks
- Clear deliverables
- No additions without discussion

**Next Step:** Start Phase 1 - Core Parser

---
*Any Claude session working on this project MUST follow this contract.*