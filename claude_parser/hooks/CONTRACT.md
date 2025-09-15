# Hook Data Contract

## What Claude-Parser Provides

### 1. HookRequest Object
```python
# Clean data object with these fields:
request.hook_event_name  # "PostToolUse", "PreToolUse", etc. (as-is from Claude Code)
request.session_id       # Session identifier
request.transcript_path  # Path to JSONL file
request.cwd             # Current working directory
request.tool_name       # Tool name (for tool events)
request.tool_input      # Tool input data
request.tool_response   # Tool response (PostToolUse)
request.conversation    # Lazy-loaded conversation dict
```

### 2. Input Data Formats
- **Accepts both**: camelCase (from Claude Code) and snake_case (for testing)
- **No transformation**: We pass `hook_event_name` exactly as received
- **No constraints**: Plugin systems can use the event name however they want

### 3. Result Aggregation
```python
# Plugins return tuples
("allow", "optional message")
("block", "reason for blocking")

# We aggregate with ANY block = fail policy
request.complete(results) -> exit_code
```

### 4. JSON Output Formats
Based on `hook_event_name`, we format the appropriate JSON per Anthropic spec:
- PostToolUse → `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "..."}}`
- PreToolUse → `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow/deny", ...}}`
- Others → As specified by Anthropic

## What We DON'T Do

1. **No string transformation** of hook_event_name
2. **No method name mapping** (that's the plugin framework's job)
3. **No plugin registration** (that's lnca-hooks' responsibility)
4. **No opinion on plugin patterns** (decorators, methods, etc.)

## Contract Guarantees

1. **Stable field names**: HookRequest attributes won't change
2. **Both formats work**: camelCase and snake_case both supported
3. **Predictable aggregation**: ANY block = exit code 2, all allow = exit code 0
4. **Correct JSON**: Output matches Anthropic's specification

## For Plugin Developers

```python
# Your plugin gets a HookRequest object
def handle_hook(request):
    # Access any field directly
    if request.tool_name == "Write":
        # Your logic here
        return ("allow", "Check passed")

    # Access conversation if needed
    messages = request.conversation.get('messages', [])
    # Use our SDK to analyze
    from claude_parser.navigation import get_latest_assistant_message
    latest = get_latest_assistant_message(messages)

    return ("block", "Reason for blocking")
```

## Summary

Claude-parser provides **clean data** and **correct aggregation**. How you register plugins, what patterns you use, and how you map event names to handlers is entirely up to your plugin framework. We don't impose any constraints on your design choices.