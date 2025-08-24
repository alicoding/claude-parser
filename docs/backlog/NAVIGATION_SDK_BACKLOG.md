# Navigation SDK Backlog

## 🎯 Core Problem We're Solving
Enable powerful navigation and querying of Claude Code JSONL conversations for memory systems, hook platforms, and development workflows.

## 🏗️ Architecture Alignment
- **Domain**: Generic JSONL navigation capabilities (NOT feature-specific)
- **Principle**: SDK provides tools, users build features
- **Philosophy**: Deep JSONL understanding with comprehensive edge case handling

## 📋 Backlog Items

### 1. Deep JSONL Structure Testing
**Priority**: HIGH - Foundation for everything else

- [ ] Test session boundary detection (`sessionId` changes)
- [ ] Test conversation threading (`parentUuid` chains)
- [ ] Test sidechain handling (`isSidechain: true`)
- [ ] Test meta message filtering (`isMeta: true`)
- [ ] Test summary-only sessions (edge case)
- [ ] Test tool use sequences and grouping
- [ ] Test multi-branch sessions (`gitBranch` changes)
- [ ] Test empty files and malformed JSON
- [ ] Test large file handling (100MB+)
- [ ] Test real-time file append scenarios

### 2. Generic Message Navigation Domain
**Priority**: HIGH - Core SDK capability

```python
class Conversation:
    # UUID-based lookup
    def get_by_uuid(self, uuid: str) -> Message | None
    def get_by_field(self, field: str, value: any) -> List[Message]
    
    # Context navigation
    def get_surrounding(self, uuid: str, before: int, after: int) -> List[Message]
    def get_thread_from(self, uuid: str) -> List[Message]
    def get_thread_to(self, uuid: str) -> List[Message]
    
    # Temporal navigation
    def get_messages_before_timestamp(self, timestamp: str) -> List[Message]
    def get_messages_after_timestamp(self, timestamp: str) -> List[Message]
    def get_messages_between_timestamps(self, start: str, end: str) -> List[Message]
    
    # Session navigation
    def get_session_boundaries(self) -> List[SessionBoundary]
    def get_sessions(self) -> List[Session]
    def filter_by_session(self, session_id: str) -> List[Message]
    
    # Threading navigation
    def get_main_thread(self) -> List[Message]  # Exclude sidechains
    def get_sidechains(self) -> List[List[Message]]
    def exclude_meta_messages(self) -> List[Message]
```

### 3. Advanced Search & Query Domain
**Priority**: MEDIUM - Enhanced discovery

```python
class ConversationQuery:
    # Multi-keyword search
    def contains_all(self, keywords: List[str]) -> List[Message]
    def contains_any(self, keywords: List[str]) -> List[Message]
    
    # Regex search
    def regex(self, pattern: str) -> List[Message]
    
    # Search with context
    def search_with_context(self, query: str, before: int, after: int) -> List[MessageContext]
    
    # Fuzzy search
    def fuzzy_search(self, query: str, threshold: float = 0.8) -> List[Message]
    
    # Field-specific search
    def search_by_type(self, message_type: str) -> List[Message]
    def search_by_branch(self, git_branch: str) -> List[Message]
    def search_by_tool(self, tool_name: str) -> List[Message]
```

### 4. File Recovery Domain
**Priority**: MEDIUM - Powerful dev workflow feature

```python
class FileRecovery:
    def get_file_versions(self, filepath: str) -> List[FileVersion]
    def get_file_at_message(self, message_uuid: str, filepath: str) -> str | None
    def get_file_before_tool(self, tool_uuid: str, filepath: str) -> str | None
    def track_file_changes(self, filepath: str) -> List[FileChange]
    def get_deleted_files(self) -> List[str]
    def restore_file_content(self, filepath: str, at_timestamp: str) -> str | None
```

### 5. Decision Tracking Domain  
**Priority**: MEDIUM - ADR and decision memory

```python
class DecisionContext:
    def find_decision_points(self, keywords: List[str]) -> List[Message]
    def get_decision_context(self, decision_uuid: str, radius: int) -> DecisionContext
    def trace_decision_evolution(self, topic: str) -> List[Message]
    def find_pivot_points(self) -> List[PivotPoint]
```

## 🎯 Use Case Examples (Don't Build - Just Document)

### Hook Platform Context Injection
```python
# Example: Provide context at SessionStart to prevent hallucination
def get_session_context():
    conv = load("session.jsonl")
    last_summary = conv.summaries()[-1] if conv.summaries() else None
    if last_summary:
        context = conv.get_surrounding(last_summary.uuid, before=20, after=0)
        return context.exclude_meta_messages()
    return conv.get_messages_before_timestamp("last_hour")
```

### PreToolUse:Bash Context
```python
# Example: Remind about SOLID/DRY/DDD principles before Bash tools
def get_architecture_reminders():
    conv = load("session.jsonl")
    architecture_decisions = conv.search("SOLID") + conv.search("DDD") + conv.search("architecture")
    return [conv.get_surrounding(msg.uuid, 1, 1) for msg in architecture_decisions[-3:]]
```

### File-Specific Decision Context
```python
# Example: Provide context when specific files are touched
def get_file_decision_context(filename: str):
    conv = load("session.jsonl")
    file_mentions = conv.search(filename)
    decisions = [msg for msg in file_mentions if "decision" in msg.text_content.lower()]
    return [conv.get_surrounding(msg.uuid, 2, 2) for msg in decisions]
```

### Memory Project Context Recovery
```python
# Example: Bridge context across session resets
def bridge_session_context(old_session: str, new_session: str):
    old_conv = load(old_session)
    important_context = old_conv.get_messages_with_errors() + old_conv.search("TODO") + old_conv.search("decision")
    return important_context[-10:]  # Last 10 important items
```

## 🔧 Technical Requirements

### JSONL Edge Case Handling
- Empty files (0 lines)
- Summary-only files (1 line)
- Malformed JSON lines (skip with logging)
- Missing optional fields (use defaults)
- Large files (streaming with orjson)
- Session boundary detection
- Thread reconstruction via parentUuid
- Sidechain filtering
- Meta message handling

### Performance Requirements
- O(1) UUID lookup via internal hash map
- Streaming for files > 100MB
- Memory efficient for large conversations
- Fast text search with indexing

### API Design Principles
- 95/5 principle: Simple for common cases, powerful for advanced
- Generic capabilities, not feature-specific
- Chainable methods for complex queries
- Rich return types with full context

## 🚀 Implementation Priority

1. **Deep JSONL Testing** - Foundation
2. **Generic Navigation** - Core capability  
3. **Advanced Search** - Enhanced discovery
4. **File Recovery** - Powerful workflow feature
5. **Decision Tracking** - Memory and ADR support

## 📚 Documentation Needed

- JSONL edge case examples with test data
- Navigation patterns and best practices
- Performance characteristics and limitations
- Integration examples for hook platforms
- Memory project integration guide