# Watch Domain API

The Watch domain provides real-time JSONL file monitoring, enabling selective message filtering and live conversation updates.

## 🚀 Quick Start (95% Use Case)

### Synchronous Watch
```python
from claude_parser.watch import watch

def on_new_messages(conv, new_messages):
    """Called whenever new messages appear in transcript."""
    for msg in new_messages:
        print(f"New {msg.type}: {msg.text_content[:50]}...")

# Start monitoring (1 line replaces 513 lines of monitoring code!)
watch("session.jsonl", on_new_messages)
```

### Asynchronous Watch (NEW)
```python
from claude_parser.watch import watch_async

async def monitor_messages():
    """Async monitoring for integration with async backends."""
    async for conv, new_messages in watch_async("session.jsonl"):
        for msg in new_messages:
            print(f"New {msg.type}: {msg.text_content[:50]}...")
            # Send via SSE, WebSocket, etc - your choice!

# Use with any async framework (FastAPI, aiohttp, Sanic, etc)
await monitor_messages()
```

This replaces complex file polling and monitoring systems with a simple, high-level API.

## ✅ Implementation Status

| Component | Status | Tests | Coverage |
|-----------|--------|-------|----------|
| watch() function | ✅ Complete | 4/4 | 100% |
| watch_async() function | ✅ Complete | 8/8 | 100% |
| Message type filtering | ✅ Complete | 1/1 | 100% |
| File rotation handling | ✅ Complete | Built-in | 100% |
| Error resilience | ✅ Complete | Built-in | 100% |
| Cross-platform support | ✅ Complete | Built-in | 100% |

---

## Core Functions (95% API)

### `watch(file_path, callback, message_types=None)` ✅ Implemented

Watch JSONL file for changes and call callback with new messages.

```python
from claude_parser.watch import watch

def my_callback(conv, new_messages):
    print(f"Got {len(new_messages)} new messages")
    for msg in new_messages:
        print(f"- {msg.type}: {msg.text_content[:50]}")

# Monitor any Claude Code JSONL file
watch("transcript.jsonl", my_callback)  # Blocks until Ctrl+C
```

**Parameters:**
- `file_path` (str): Path to JSONL file to monitor
- `callback` (callable): Function called with (Conversation, List[Message])
- `message_types` (List[str], optional): Filter messages ["user", "assistant", "tool_use"]

**Returns:** None (blocks until KeyboardInterrupt)

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `PermissionError`: If file can't be read

**Performance:** 
- Memory usage independent of file size
- Detects changes within ~100ms
- Handles GB+ files efficiently

### `watch_async(file_path, message_types=None, stop_event=None)` ✅ Implemented

Asynchronously watch JSONL file for changes using async generators.

```python
from claude_parser.watch import watch_async
import asyncio

async def main():
    async for conv, new_messages in watch_async("transcript.jsonl"):
        print(f"Got {len(new_messages)} new messages")
        for msg in new_messages:
            print(f"- {msg.type}: {msg.text_content[:50]}")

# Run with any async framework
asyncio.run(main())
```

**Parameters:**
- `file_path` (str | Path): Path to JSONL file to monitor
- `message_types` (List[str], optional): Filter messages ["user", "assistant", "tool_use"]
- `stop_event` (asyncio.Event, optional): Event to stop watching

**Yields:** AsyncGenerator of (Conversation, List[Message]) tuples

**Performance:**
- Uses watchfiles.awatch internally (Rust-based, runs in separate thread)
- No manual threading needed
- Same ~100ms detection latency as sync version

**Integration Examples:**

```python
# FastAPI
@app.get("/stream")
async def stream():
    async def generate():
        async for conv, new_messages in watch_async("session.jsonl"):
            for msg in new_messages:
                yield format_sse(msg)
    return EventSourceResponse(generate())

# aiohttp
async def stream_handler(request):
    response = web.StreamResponse()
    await response.prepare(request)
    async for conv, new_messages in watch_async("session.jsonl"):
        for msg in new_messages:
            await response.write(json.dumps(msg).encode())
    return response
```

---

## Message Type Filtering

Filter to only the message types you care about:

### Monitor Only Assistant Responses
```python
def on_assistant_messages(conv, new_messages):
    for msg in new_messages:
        print(f"🤖 Assistant: {msg.text_content}")
        
        if msg.has_errors():
            print(f"❌ Error: {msg.error_content}")

watch("session.jsonl", on_assistant_messages, message_types=["assistant"])
```

### Monitor Tool Usage
```python
def on_tool_activity(conv, new_messages):
    for msg in new_messages:
        if msg.type == "tool_use":
            print(f"🔧 Tool: {msg.tool_name}")
            if msg.tool_name == "Bash":
                print(f"⚠️  Command: {msg.tool_input.get('command', '')}")

watch("session.jsonl", on_tool_activity, message_types=["tool_use", "tool_result"])
```

### Monitor Multiple Types
```python
def on_conversation_flow(conv, new_messages):
    for msg in new_messages:
        if msg.type == "user":
            print(f"👤 User: {msg.content}")
        elif msg.type == "assistant":  
            print(f"🤖 Assistant: {msg.text_content}")

watch("session.jsonl", on_conversation_flow, message_types=["user", "assistant"])
```

---

## Real-World Use Cases

### 1. Development Dashboard
Real-time development monitoring:

```python
from claude_parser.watch import watch
from collections import defaultdict
import time

# Track metrics in real-time
stats = {
    "messages": 0,
    "tools": defaultdict(int),
    "errors": 0,
    "start_time": time.time()
}

def update_dashboard(conv, new_messages):
    """Live development statistics."""
    for msg in new_messages:
        stats["messages"] += 1
        
        if msg.type == "tool_use":
            stats["tools"][msg.tool_name] += 1
        
        if msg.has_errors():
            stats["errors"] += 1
    
    # Live stats display
    duration = int(time.time() - stats["start_time"])
    print(f"\r📊 {stats['messages']} msgs | "
          f"🔧 {sum(stats['tools'].values())} tools | "
          f"❌ {stats['errors']} errors | "
          f"⏱️  {duration}s", end="")

watch("coding_session.jsonl", update_dashboard)
```

### 2. Error Detection System
Catch and alert on errors as they happen:

```python
def error_monitor(conv, new_messages):
    """Alert on any errors in real-time."""
    for msg in new_messages:
        if msg.type == "assistant" and msg.has_errors():
            error_info = {
                "timestamp": msg.timestamp,
                "error": msg.error_content,
                "session": conv.session_id
            }
            
            # Send to monitoring system
            print(f"🚨 ERROR DETECTED: {error_info}")
            send_alert_to_slack(error_info)  # Your alerting system

watch("production_session.jsonl", error_monitor)
```

### 3. Hook Integration (Smart Context)
Use with hook scripts for intelligent tool control:

```python
# In your hook script: smart_hook.py
from claude_parser.watch import watch
from claude_parser.hooks import hook_input, exit_block, exit_success
import threading

def start_monitoring():
    """Monitor session for patterns in background."""
    def pattern_monitor(conv, new_messages):
        for msg in new_messages:
            if msg.type == "tool_use" and msg.tool_name == "Bash":
                # Count recent bash commands
                recent_bash = len([m for m in conv.recent(20) 
                                 if m.type == "tool_use" and m.tool_name == "Bash"])
                
                if recent_bash > 10:
                    print("⚠️  Warning: High bash usage detected", file=sys.stderr)
    
    # Start background monitoring
    data = hook_input()
    thread = threading.Thread(target=lambda: watch(data.transcript_path, pattern_monitor))
    thread.daemon = True
    thread.start()

# Hook logic
data = hook_input()
if data.hook_type == "PreToolUse":
    start_monitoring()  # Begin background pattern detection
    exit_success()
```

### 4. Team Collaboration Dashboard
Monitor multiple team members' Claude sessions:

```python
from pathlib import Path
import json

team_activity = {}

def create_member_monitor(member_name):
    """Create monitoring function for team member."""
    def monitor_member(conv, new_messages):
        if member_name not in team_activity:
            team_activity[member_name] = {
                "messages": 0, 
                "tools": 0, 
                "last_activity": None
            }
        
        activity = team_activity[member_name]
        activity["messages"] += len(new_messages)
        activity["tools"] += len([m for m in new_messages if m.type == "tool_use"])
        
        if new_messages:
            activity["last_activity"] = new_messages[-1].timestamp
        
        # Update team dashboard
        with open("team_dashboard.json", "w") as f:
            json.dump(team_activity, f, indent=2)
    
    return monitor_member

# Monitor team sessions
sessions_dir = Path("~/.claude/team/").expanduser()
for session_file in sessions_dir.glob("*.jsonl"):
    member = session_file.stem
    monitor_func = create_member_monitor(member)
    
    # Start monitoring each member's session
    threading.Thread(
        target=lambda: watch(str(session_file), monitor_func),
        daemon=True
    ).start()
```

### 5. Memory System Integration  
Real-time knowledge extraction:

```python
# Requires: pip install mem0
from mem0 import MemoryClient

memory = MemoryClient()

def extract_to_memory(conv, new_messages):
    """Extract insights to long-term memory."""
    for msg in new_messages:
        if msg.type == "assistant":
            content = msg.text_content
            
            # Extract learnings
            if any(keyword in content.lower() for keyword in ["learned", "discovered", "insight"]):
                memory.add(content, user_id="claude_session")
            
            # Extract code patterns
            if msg.has_code_blocks():
                for block in msg.code_blocks:
                    memory.add(
                        f"Code pattern: {block.code}", 
                        metadata={"type": "code", "language": block.language}
                    )

watch("learning_session.jsonl", extract_to_memory)
```

### 6. Quality Assurance Monitor
Automated QA and testing:

```python
import subprocess

def qa_monitor(conv, new_messages):
    """Quality assurance monitoring."""
    for msg in new_messages:
        # Check tool failures
        if msg.type == "tool_result" and not msg.success:
            print(f"🔴 Tool failure: {msg.tool_name} - {msg.error}")
        
        # Check for code syntax
        if msg.type == "assistant" and msg.has_code_blocks():
            for block in msg.code_blocks:
                if block.language == "python":
                    try:
                        compile(block.code, "<claude_code>", "exec")
                    except SyntaxError as e:
                        print(f"🐍 Python syntax error: {e}")
                        
        # Run tests automatically when test files are created
        if (msg.type == "tool_use" and 
            msg.tool_name == "Write" and 
            "test_" in msg.tool_input.get("file_path", "")):
            
            print("🧪 Test file created, running tests...")
            subprocess.run(["pytest", "-v"], capture_output=True)

watch("development_session.jsonl", qa_monitor)
```

---

## Advanced Features

### File Rotation Handling
The watcher automatically handles file rotation and truncation:

```python
def robust_monitor(conv, new_messages):
    """Handles file rotation gracefully."""
    print(f"Processed {len(new_messages)} new messages")
    # File rotation/truncation handled automatically

# Works even with log rotation, file replacement, etc.
watch("rotating_session.jsonl", robust_monitor)
```

### Error Resilience
Malformed JSON lines don't crash the watcher:

```python
def resilient_monitor(conv, new_messages):
    """Only valid messages reach the callback."""
    # new_messages contains only successfully parsed messages
    # Malformed JSON lines are logged to stderr but don't crash
    for msg in new_messages:
        print(f"Valid message: {msg.type}")

watch("potentially_corrupted.jsonl", resilient_monitor)
```

### Performance Optimization
Memory usage stays constant regardless of file size:

```python
def performance_monitor(conv, new_messages):
    """Efficient monitoring of large files."""
    # Only new messages are parsed and loaded into memory
    # Full conversation is loaded fresh each time (consistent state)
    # Memory usage independent of total file size
    print(f"Monitoring file with {len(conv)} total messages")
    print(f"Processing {len(new_messages)} new messages")

# Handles GB+ files efficiently
watch("massive_session.jsonl", performance_monitor)
```

---

## Integration with Other Domains

### With Parser Domain
```python
from claude_parser import load
from claude_parser.watch import watch

def analyze_changes(conv, new_messages):
    """Analyze conversation patterns."""
    # conv is a full Conversation object with all methods
    recent_errors = conv.with_errors()
    user_messages = conv.user_messages
    
    print(f"Total: {len(conv)} messages")
    print(f"Errors: {len(recent_errors)} errors") 
    print(f"New: {len(new_messages)} new messages")

watch("session.jsonl", analyze_changes)
```

### With Hooks Domain
```python
from claude_parser.hooks import hook_input, exit_success
from claude_parser.watch import watch
import threading

def hook_with_monitoring():
    """Hook script that starts background monitoring."""
    data = hook_input()
    
    def background_monitor(conv, new_messages):
        # Monitor patterns while hook is active
        print(f"Background: {len(new_messages)} new messages")
    
    # Start background monitoring
    monitor_thread = threading.Thread(
        target=lambda: watch(data.transcript_path, background_monitor)
    )
    monitor_thread.daemon = True
    monitor_thread.start()
    
    exit_success()
```

---

## Error Handling

### Common Patterns
```python
def safe_monitor(conv, new_messages):
    """Handle errors gracefully."""
    try:
        for msg in new_messages:
            # Your processing logic
            process_message(msg)
    except Exception as e:
        print(f"Processing error: {e}", file=sys.stderr)
        # Continue monitoring despite errors

# Watcher continues running even if callback raises exceptions
watch("session.jsonl", safe_monitor)
```

### File System Errors
```python
try:
    watch("session.jsonl", my_callback)
except FileNotFoundError:
    print("Session file not found - waiting for session to start...")
    # Implement retry logic or file creation waiting
except PermissionError:
    print("Permission denied - check file permissions")
except KeyboardInterrupt:
    print("Monitoring stopped by user")
```

---

## Performance Characteristics

| Metric | Performance |
|--------|-------------|
| **Change Detection** | < 100ms latency |
| **Memory Usage** | Independent of file size |
| **File Size Support** | GB+ files supported |
| **CPU Overhead** | Minimal (event-driven) |
| **Cross-Platform** | macOS, Linux, Windows |

---

## Technical Architecture

### Single Responsibility Design
- **`watch()`**: High-level file monitoring interface
- **`IncrementalReader`**: File position tracking and change detection  
- **`_parse_new_messages()`**: JSON parsing and message filtering
- **Integration**: Uses Parser and Models domains for data handling

### Library-First Approach
- **watchfiles**: Cross-platform file monitoring (Rust-based)
- **orjson**: High-performance JSON parsing  
- **pydantic**: Message validation and typing
- **No custom file polling**: Uses native OS file events

### Error Boundaries
- JSON parsing errors don't crash watcher
- File system errors are reported but monitoring continues
- Callback exceptions don't stop file monitoring
- Graceful handling of file rotation/truncation

---

## See Also

- [Parser Domain](./parser.md) - Load conversations from watch callbacks
- [Hooks Domain](./hooks.md) - Use watcher in hook scripts  
- [Models](./models.md) - Message types and structure
- [Quick Reference](./QUICK_REFERENCE.md) - One-page API summary