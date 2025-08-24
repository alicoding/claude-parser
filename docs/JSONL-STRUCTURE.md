# Claude Code JSONL Structure Reference

## Quick Reference for Claude Parser SDK

This document serves as the primary reference for understanding Claude Code's JSONL structure.
When you don't know something about JSONL format, **check here first**.

## Core Message Structure

> **🔴 IMPORTANT**: See [JSONL_STRUCTURE_COMPLETE.md](./JSONL_STRUCTURE_COMPLETE.md) for the COMPLETE auto-discovered structure from 41,085 real messages, including token usage fields!

Every line in a Claude JSONL file is a JSON object with these fields:

```typescript
{
  // Session & Threading
  "uuid": string,              // Unique message ID
  "parentUuid": string | null, // Parent message for threading
  "sessionId": string,         // Session identifier (changes without --resume/--continue)
  
  // Context
  "cwd": string,               // Current working directory
  "gitBranch": string,         // Git branch (empty if not in repo)
  "version": string,           // Claude Code version (e.g., "1.0.83")
  
  // Message Content
  "type": "user" | "assistant" | "system" | "summary",  // NO tool_use/tool_result here!
  "message": {
    "role": string,
    "content": string | ContentBlock[],
    // Assistant messages include:
    "id"?: string,
    "model"?: string,
    "usage"?: {  // TOKEN TRACKING AVAILABLE!
      "input_tokens": number,
      "output_tokens": number,
      "cache_creation_input_tokens": number,
      "cache_read_input_tokens": number
    }
  },
  
  // Metadata
  "timestamp": string,         // ISO 8601 timestamp
  "isSidechain": boolean,      // If true, part of parallel exploration
  "userType": "external",      // User type
  "isMeta"?: boolean,          // Meta messages (system notifications)
  
  // Request tracking (assistant messages)
  "requestId"?: string         // API request ID
}
```

## Edge Cases & Test Scenarios

### 1. Empty Session (1 line)
**File**: Single summary line only
```json
{"type":"summary","summary":"Brief description","leafUuid":"..."}
```
**Test for**: Parser handling minimal data

### 2. New Session (no --resume/--continue)
**Characteristics**:
- Different `sessionId` from previous session
- `parentUuid: null` for first message
- Often starts with system meta message
**Test for**: Session boundary detection

### 3. System-Only Messages
**Pattern**: Messages with `isMeta: true`
```json
{"isMeta":true,"type":"user","message":{"role":"user","content":"DO NOT respond..."}}
```
**Test for**: Meta message filtering

### 4. Tool Use Sequences
**Pattern**: 
1. `type: "assistant"` with tool_use content block
2. `type: "tool_result"` with tool output
3. Continues...
**Test for**: Tool operation grouping

### 5. Different Git Branches
**Pattern**: Same sessionId but different `gitBranch` values
**Test for**: Branch context tracking

### 6. Sidechains
**Pattern**: `isSidechain: true`
**Test for**: Parallel exploration handling

## Common Patterns

### Session Start Pattern
```json
// Line 1: System meta message
{"parentUuid":null,"isMeta":true,"type":"user"...}
// Line 2: User's first message or command
{"parentUuid":"<uuid-1>","type":"user"...}
// Line 3: Assistant's response
{"parentUuid":"<uuid-2>","type":"assistant"...}
```

### Tool Use Pattern
```json
// Assistant initiates tool
{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash"...}]}}
// Tool result
{"type":"tool_result","message":{"content":"output"}}
// Assistant continues
{"type":"assistant","message":{"content":[{"type":"text","text":"Based on..."}]}}
```

## Finding Test Data

### Minimal Sessions (Edge Cases)
```bash
# Find sessions with only 1-5 lines (edge cases)
for file in ~/.claude/projects/*/*.jsonl; do 
  lines=$(wc -l < "$file")
  [ $lines -le 5 ] && echo "$lines $file"
done | sort -n
```

### Real Sessions by Size
```bash
# Small (testing quick operations)
find ~/.claude/projects -name "*.jsonl" -size -100k

# Medium (typical sessions)
find ~/.claude/projects -name "*.jsonl" -size +100k -size -1M

# Large (stress testing)
find ~/.claude/projects -name "*.jsonl" -size +10M
```

### Sessions with Specific Patterns
```bash
# Find sessions with tool use
grep -l "tool_use" ~/.claude/projects/*/*.jsonl

# Find sessions with errors
grep -l "error" ~/.claude/projects/*/*.jsonl

# Find multi-branch sessions
for f in ~/.claude/projects/*/*.jsonl; do
  branches=$(jq -r '.gitBranch' "$f" 2>/dev/null | sort -u | wc -l)
  [ $branches -gt 1 ] && echo "$f has $branches branches"
done
```

## Critical Fields for Testing

| Field | Edge Cases | Why Test |
|-------|------------|----------|
| `sessionId` | Changes without --resume | Session boundary detection |
| `parentUuid` | null for first message | Threading validation |
| `gitBranch` | Empty for non-git dirs | Context tracking |
| `isSidechain` | Parallel explorations | Sidechain filtering |
| `isMeta` | System messages | Meta message handling |
| `type` | "summary" type | Summary detection |
| `message.content` | String vs Array | Content normalization |

## Parser Requirements

The Claude Parser SDK must handle:

1. **Empty files** - Gracefully handle 0-line files
2. **Summary-only files** - Parse single summary line
3. **Malformed JSON** - Skip bad lines with error logging
4. **Missing fields** - Use defaults for optional fields
5. **Large files** - Stream processing for 100MB+ files
6. **Real-time updates** - Handle file appends during parsing
7. **Session boundaries** - Detect sessionId changes
8. **Threading** - Reconstruct conversation threads via parentUuid

## Quick Debug Commands

```bash
# Check if valid JSONL
jq -c . < file.jsonl > /dev/null && echo "Valid" || echo "Invalid"

# Count message types
jq -r '.type' file.jsonl | sort | uniq -c

# Extract session IDs
jq -r '.sessionId' file.jsonl | sort -u

# Find tool operations
jq -r 'select(.type == "tool_use" or .type == "tool_result")' file.jsonl
```

## Remember

- **Always test with real files** from `~/.claude/projects/`
- **Edge cases are common** - empty sessions, single messages, etc.
- **SessionId changes** indicate new conversation threads
- **ParentUuid chains** create the conversation tree
- **Summary messages** may be the only content in short sessions