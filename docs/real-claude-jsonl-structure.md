# Real Claude Code JSONL Structure Analysis

Based on authentic Claude Code sessions generated in `/Users/ali/.claude/projects/-private-tmp-claude-parser-test-project/`

## Key Discoveries

### 1. Multi-Session Reality
- **Two separate JSONL files** for same project path
- Each file represents a different Claude Code session
- Session IDs: `0c9f3362-4b85-4861-a604-6ef1578e2aa2` and `94aeb5b2-3063-496a-9965-9e2dfcd59043`

### 2. Real JSONL Structure

```json
{
  "parentUuid": "b842e6a2-cca5-4a0f-8b00-e9d7161dbd2c",
  "isSidechain": false,
  "userType": "external",
  "cwd": "/private/tmp/claude-parser-test-project",
  "sessionId": "0c9f3362-4b85-4861-a604-6ef1578e2aa2",
  "version": "1.0.103",
  "gitBranch": "",
  "type": "assistant",
  "message": {
    "content": [
      {
        "type": "tool_use",
        "id": "toolu_016ivExHYAemketd9zGuzQDb",
        "name": "Edit",
        "input": {
          "file_path": "/private/tmp/claude-parser-test-project/hello.py",
          "old_string": "print(\"initial\")",
          "new_string": "print(\"Hello World\")"
        }
      }
    ]
  },
  "uuid": "b3116673-12ae-42ee-9f9a-daff87652161",
  "timestamp": "2025-09-04T05:30:59.532Z"
}
```

### 3. Critical Fields for claude-parser

- **uuid**: Primary identifier for navigation
- **parentUuid**: Chain linking for conversation flow
- **sessionId**: Critical for multi-session handling
- **timestamp**: For chronological ordering across sessions
- **message.content[].input**: Contains actual tool parameters
- **cwd**: Working directory context

### 4. Tool Operations Found

- **Read**: `{"name": "Read", "input": {"file_path": "..."}}`
- **Edit**: `{"name": "Edit", "input": {"file_path": "...", "old_string": "...", "new_string": "..."}}`
- **Permission Errors**: Tool results show permission handling

## Implications for claude-parser

### Discovery Service Must:
1. Handle multiple JSONL files per project directory
2. Aggregate operations across sessions chronologically
3. Use `sessionId` for session tracking
4. Parse actual Claude project path encoding

### Timeline Service Must:
1. Process real tool_use message structure
2. Handle parentUuid chains for operation ordering
3. Merge multi-session data correctly
4. Extract file operations from message.content arrays

### Multi-Session Concurrency:
- **Problem**: Same file modified in different sessions
- **Solution**: Use timestamps + sessionId for conflict resolution
- **Navigation**: Must work across session boundaries

## Next Steps

Replace all fake JSONL fixtures with this real structure throughout the codebase.
