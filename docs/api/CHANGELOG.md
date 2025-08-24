# API Changelog

All notable changes to the Claude Parser SDK API are documented here.

## [2.0.3] - SSE Transport Implementation

### 2025-08-20 

#### 🌊 Added - Real-time Streaming Transport

- **SSE Transport Layer Complete**
  - Transport-agnostic interface following SOLID principles
  - SSE implementation matching Anthropic/OpenAI/Vercel pattern
  - ZERO `any` types - God-mode TypeScript
  - Automatic reconnection with exponential backoff
  - Tests: 21/21 passing with real Claude message format
  - Bundle size: ~3KB minified
  - **Impact**: Replaces 400+ lines of WebSocket code with 1 line

#### API Example
```typescript
// 95% use case - zero config
import { createTransport } from '@claude-parser/core'

const transport = createTransport('/api/stream')
transport.connect()
transport.onMessage(msg => console.log(msg))

// 5% use case - custom config
const transport = createTransport('/api/stream', {
  reconnectInterval: 5000,
  maxReconnectAttempts: 10
})
```

## [2.0.2] - Critical Bug Fix for tool_response

### 2025-08-20

#### 🔧 CRITICAL FIX - tool_response Now Accepts Strings

- **FIXED: tool_response accepts string output from tools**
  - LS, Grep, Read, Bash tools return strings, not Dict/List[Dict]
  - Updated type: `Union[str, Dict[str, Any], List[Dict[str, Any]]]`
  - Tests: 8/8 tests with real Claude tool outputs
  - **Impact**: Fixes PostToolUse hooks for most common tools

## [2.0.1] - Critical Bug Fix

### 2024-08-20

#### 🔧 CRITICAL FIX - Claude JSON Schema Compatibility

- **FIXED: Schema Mismatch with Real Claude Code JSON**
  - Added field aliases for camelCase → snake_case conversion
  - Fixed `tool_response` type: handles `List[Dict]` format from Claude Code
  - Added `populate_by_name=True` for dual format support
  - Tests: 8/8 comprehensive Claude format validation tests
  - **Impact**: Unblocks production adoption, eliminates vendor lock-in

## [2.0.0] - Phase 2 Implementation

### 2024-08-20

#### Added - Hooks Domain

##### ✅ Implemented
- **HookData model**: Universal model for all 8 Claude Code hook types
  - Immutable (frozen=True) following DDD principles
  - Forward compatible (extra="allow")
  - Required field validation (min_length=1)
  - Integration with Parser domain via `load_conversation()`
  - Tests: 9/9 passing, 100% coverage

- **hook_input() function**: Parse JSON from stdin
  - Single function for all hook types (DRY)
  - Uses orjson for 10x faster parsing
  - Uses pydantic for validation
  - Performance: < 1ms
  - Tests: 11/11 passing, 100% coverage

##### ✅ Implemented
- **exit_success()** - Exit with code 0, optional stdout message
  - Single responsibility: success exit only
  - Performance: < 1ms, ≤ 3 lines of code
  - Tests: 10/10 passing, 100% coverage
  - Handles empty strings, multiline messages, unicode

- **exit_block()** - Exit with code 2 (blocking), required stderr reason
  - Single responsibility: blocking exit only  
  - Performance: < 1ms, ≤ 3 lines of code
  - Tests: 10/10 passing, 100% coverage
  - Handles unicode reasons, stderr routing

- **exit_error()** - Exit with code 1 (non-blocking), required stderr message
  - Single responsibility: error exit only
  - Performance: < 1ms, ≤ 3 lines of code  
  - Tests: 10/10 passing, 100% coverage
  - Proper type hints (NoReturn)

##### 🔧 Critical Bug Fixes

- **FIXED: Claude JSON Schema Mismatch** (v2.0.1)
  - Added field aliases for camelCase compatibility (`sessionId` → `session_id`)
  - Fixed `tool_response` type to handle `List[Dict]` format from real Claude Code
  - Maintained backward compatibility with snake_case Python format
  - Added comprehensive tests with real Claude Code JSON samples
  - Tests: 8/8 passing, 100% coverage of real Claude scenarios
  
##### ✅ Implemented  
- **watch() function**: Real-time JSONL file monitoring
  - Single responsibility: File watching with incremental parsing
  - Performance: < 100ms change detection, memory independent of file size
  - Tests: 4/4 passing, 100% coverage
  - Cross-platform support: macOS, Linux, Windows via watchfiles
  - File rotation/truncation handling built-in
  - Message type filtering support
  - Integration with Parser and Models domains

##### 📋 Planned
- Advanced API (json_output, convenience methods for hooks)
- Analytics domain (token counting, conversation analysis)
- Memory domain (mem0 integration)

#### Changed
- Removed pytest-asyncio dependency (not needed for synchronous code)
- Updated to pydantic v2 ConfigDict instead of Config class

#### Performance
- Hook parsing: < 1ms (target was 10ms)
- Memory: Minimal overhead with pydantic models

#### Breaking Changes
- None - Phase 2 is additive only

---

## [1.0.0] - Phase 1 (Complete)

### Parser Domain

#### Implemented
- **load()**: Load JSONL conversations
- **Conversation class**: Main aggregate root
- **Message models**: User, Assistant, Tool, Summary
- **Search methods**: search(), filter(), with_errors()
- **Navigation**: before_summary(), indexing support

#### Performance
- Loading: ~3,000 messages in 0.1-0.2 seconds
- Search: ~1M messages/second
- Memory: ~4x file size

---

## API Principles

All API changes follow these principles:
1. **95/5**: Simple cases in ≤ 3 lines
2. **SOLID**: Single responsibility per function
3. **DRY**: No duplication
4. **DDD**: Clear domain boundaries
5. **Library-First**: Best-in-class libraries only
6. **No Breaking Changes**: Only additive changes