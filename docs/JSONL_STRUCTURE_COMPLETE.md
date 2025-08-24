# Claude Code JSONL Complete Structure Reference

## Auto-Discovered from 41,085 Real Messages

This document contains the COMPLETE structure discovered from analyzing actual Claude Code JSONL files.

## Core Message Structure (Updated)

```typescript
interface ClaudeMessage {
  // Session & Threading
  uuid: string;                    // Unique message ID
  parentUuid: string | null;       // Parent for threading (null for first message)
  sessionId: string;               // Session identifier (changes without --resume)
  
  // Context
  cwd: string;                     // Current working directory
  gitBranch: string;               // Git branch (can be empty string)
  version: string;                 // Claude Code version (e.g., "1.0.83")
  
  // Message Type & Content
  type: "user" | "assistant" | "system" | "summary";  // No tool_use/tool_result at root!
  message?: {                      // Present for user/assistant messages
    role: string;
    content: string | ContentBlock[];
    id?: string;                  // Assistant messages
    model?: string;               // Assistant messages (e.g., "claude-3-5-sonnet-20241022")
    usage?: UsageInfo;            // Token usage (assistant messages only)
  };
  
  // System Messages
  content?: string;                // System messages use this instead of message
  level?: "info" | "error";        // System message level
  
  // Tool-Related
  toolUseID?: string;              // Links tool use to result
  toolUseResult?: any;             // Tool execution result
  
  // Metadata
  timestamp: string;               // ISO 8601 timestamp
  isSidechain: boolean;            // Parallel exploration flag
  userType: "external";            // Always "external" in user files
  isMeta?: boolean;                // Meta messages flag
  isCompactSummary?: boolean;      // Compact summary flag
  isApiErrorMessage?: boolean;     // API error flag
  
  // Request Tracking
  requestId?: string;              // API request ID (assistant messages)
  
  // Summary Fields
  summary?: string;                // Summary text (type="summary" only)
  leafUuid?: string;               // Last message UUID (summary only)
}
```

## Token Usage Structure (DISCOVERED!)

```typescript
interface UsageInfo {
  // Core token counts
  input_tokens: number;                    // Tokens in the input
  output_tokens: number;                   // Tokens generated
  
  // Cache usage (CRITICAL for token economy!)
  cache_creation_input_tokens: number;     // Tokens added to cache
  cache_read_input_tokens: number;         // Tokens read from cache
  
  // Detailed cache breakdown
  cache_creation?: {
    ephemeral_5m_input_tokens: number;    // 5-minute cache
    ephemeral_1h_input_tokens: number;    // 1-hour cache
  };
  
  // Service information
  service_tier?: "standard" | "premium";
  
  // Tool usage tracking
  server_tool_use?: {
    web_search_requests: number;          // Web searches performed
  };
}
```

## Content Block Types

```typescript
type ContentBlockType = 
  | "text"         // Regular text content (12,285 occurrences)
  | "tool_use"     // Tool invocation (9,102 occurrences)
  | "tool_result"  // Tool output (9,102 occurrences)
  | "thinking"     // Claude's thinking process (508 occurrences)
  | "image"        // Image content (16 occurrences)
```

## Tool Names Discovered

Most frequently used tools:
1. **Bash** - 2,351 uses
2. **Edit** - 1,348 uses
3. **Read** - 1,109 uses
4. **TodoWrite** - 1,103 uses
5. **Write** - 499 uses
6. **mcp__desktop-commander__read_file** - 494 uses (MCP tool!)
7. **mcp__desktop-commander__edit_block** - 406 uses
8. **Grep** - 348 uses
9. **mcp__desktop-commander__start_process** - 324 uses
10. **mcp__desktop-commander__search_code** - 263 uses

## Message Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| assistant | 17,053 | 41.5% |
| system | 12,049 | 29.3% |
| user | 11,942 | 29.1% |
| summary | 41 | 0.1% |

## Field Occurrence Rates

| Field | Occurrence Rate | Notes |
|-------|-----------------|-------|
| uuid, cwd, sessionId, timestamp | 100% | Always present |
| parentUuid | 100% | But can be null |
| message | 70.6% | Not in system messages |
| content | 29.3% | System messages only |
| toolUseID | 29.1% | Tool-related messages |
| requestId | 41.2% | Assistant messages |
| isMeta | 29.4% | Meta messages |

## Critical Discoveries

### 1. No `tool_use` or `tool_result` Message Types!
These are **content block types**, not message types. Tool operations appear as:
- `type: "assistant"` with `tool_use` content block
- Followed by `type: "assistant"` with `tool_result` content block

### 2. Token Tracking is Available
Every assistant message includes detailed token usage:
- Input/output tokens
- Cache creation and read tokens
- Ephemeral cache breakdown (5m/1h)

### 3. MCP Tools are Namespaced
MCP tools follow pattern: `mcp__<server>__<tool>`
- Example: `mcp__desktop-commander__read_file`

### 4. System Messages Use Different Structure
System messages don't have `message` field, they use:
- `content` directly at root level
- `level` field for severity

## Calculating Total Tokens in a Session

```python
from claude_parser import load

def calculate_session_tokens(transcript_path: str) -> dict:
    """Calculate total token usage for a session."""
    conv = load(transcript_path)
    
    totals = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cache_read': 0,
        'cache_created': 0,
        'total_cost': 0.0  # Can calculate cost
    }
    
    for msg in conv.assistant_messages:
        if hasattr(msg, 'message') and msg.message.get('usage'):
            usage = msg.message['usage']
            totals['input_tokens'] += usage.get('input_tokens', 0)
            totals['output_tokens'] += usage.get('output_tokens', 0)
            totals['cache_read'] += usage.get('cache_read_input_tokens', 0)
            totals['cache_created'] += usage.get('cache_creation_input_tokens', 0)
    
    # Total tokens processed
    totals['total_tokens'] = (
        totals['input_tokens'] + 
        totals['output_tokens'] + 
        totals['cache_read'] + 
        totals['cache_created']
    )
    
    return totals
```

## Edge Cases Found

1. **Compact Summaries**: Messages with `isCompactSummary: true`
2. **API Errors**: Messages with `isApiErrorMessage: true`
3. **Sidechains**: Parallel explorations with `isSidechain: true`
4. **Empty Git Branch**: Non-git directories have `gitBranch: ""`
5. **Thinking Blocks**: Assistant's reasoning in `thinking` content blocks

## Parser Implementation Requirements

Based on discoveries, the parser MUST:

1. **Handle Variable Structure**: System messages differ from user/assistant
2. **Parse Token Usage**: Extract all usage fields for token tracking
3. **Support MCP Tools**: Handle namespaced tool names
4. **Process Content Blocks**: Parse array of content blocks with different types
5. **Track Cache Usage**: Essential for understanding token economy
6. **Handle Nullables**: parentUuid, various optional fields

## Sample Real Message

```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "parentUuid": "z9y8x7w6-v5u4-3210-zyxw-vu9876543210",
  "sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
  "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center",
  "gitBranch": "main",
  "version": "1.0.83",
  "type": "assistant",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "text",
        "text": "I'll help you fix that issue."
      },
      {
        "type": "tool_use",
        "id": "toolu_01ABC123",
        "name": "Read",
        "input": {
          "file_path": "/path/to/file.py"
        }
      }
    ],
    "model": "claude-3-5-sonnet-20241022",
    "usage": {
      "input_tokens": 1234,
      "output_tokens": 567,
      "cache_creation_input_tokens": 41837,
      "cache_read_input_tokens": 25259,
      "cache_creation": {
        "ephemeral_5m_input_tokens": 41837,
        "ephemeral_1h_input_tokens": 0
      }
    }
  },
  "timestamp": "2025-08-22T12:34:56.789Z",
  "isSidechain": false,
  "userType": "external",
  "requestId": "req_ABC123XYZ"
}
```

## Next Steps for Claude Parser

1. **Update models** to include all discovered fields
2. **Add token tracking** methods to Conversation class
3. **Support MCP tools** in tool analysis
4. **Handle system messages** properly
5. **Implement cache analysis** for token economy optimization