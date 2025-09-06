# Test Coverage Map - ACTUAL Domains from Codebase

## 📋 Real Domain Structure (Based on `claude_parser.__init__.py`)

### **Core Conversation Domain** (`tests/conversation/`)
**Main API Features - 95% use case:**
- [ ] `load()` - Load single conversation
- [ ] `load_many()` - Load multiple conversations
- [ ] `load_large()` - Load large conversation files
- [ ] `analyze()` - Basic conversation analysis
- [ ] `extract_assistant_messages_between()` - Message filtering

**Domain Objects:**
- [ ] `Conversation` class
- [ ] `ConversationMetadata` class
- [ ] Message types (`UserMessage`, `AssistantMessage`, etc.)

### **Discovery Domain** (`tests/discovery/`)
**Discovery Features:**
- [ ] `find_current_transcript()` - Current session discovery
- [ ] `find_transcript_for_cwd()` - Directory-based discovery

### **Watch Domain** (`tests/watch/`)
**Real-time Features:**
- [ ] `watch()` - Sync file watching
- [ ] `watch_async()` - Async file watching
- [ ] `stream_for_sse()` - SSE streaming
- [ ] `create_sse_stream()` - SSE stream creation

### **Analytics Domain** (`tests/analytics/`)
**Analysis Features:**
- [ ] `ConversationAnalytics` - Conversation analysis
- [ ] `TokenCounter` - Token counting

### **TODO Domain** (`tests/todo/`)
**TODO Management Features (from `domain/todo/`):**
- [ ] TODO parsing from conversations
- [ ] TODO display and formatting
- [ ] TODO management and storage
- [ ] TODO swiper functionality

### **Hooks Domain** (`tests/hooks/`)
**Hook Features (from `hooks/`):**
- [ ] Input hooks
- [ ] Output hooks
- [ ] Exit hooks
- [ ] JSON output processing

### **Features Domain** (`tests/features/`)
**Feature Registry (from `features/`):**
- [ ] Feature registration and management
- [ ] Plugin-like feature system

## 🎯 Corrected Domain Organization

### **Primary Domains (Public API)**
1. **Conversation** - Core load/analyze functionality (95% use case)
2. **Discovery** - Transcript discovery
3. **Watch** - Real-time monitoring
4. **Analytics** - Analysis tools

### **Secondary Domains (Internal Features)**
5. **TODO** - TODO management from conversations
6. **Hooks** - Hook system for extensibility
7. **Features** - Feature management system

## 📊 Test Structure Mapping

```
tests/
├── conversation/       # Core API: load(), analyze(), Conversation
├── discovery/         # find_current_transcript(), find_transcript_for_cwd()
├── watch/            # watch(), watch_async(), SSE
├── analytics/        # ConversationAnalytics, TokenCounter
├── todo/             # TODO parsing, display, management
├── hooks/            # Input/output/exit hooks
└── features/         # Feature registry system
```

This matches the ACTUAL codebase structure and public API exports!
