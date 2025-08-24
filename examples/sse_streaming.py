#!/usr/bin/env python3
"""
95/5 Solution: SSE Streaming with claude-parser

This example shows how to create a production-ready SSE endpoint
with just a few lines of code. No manual threading needed!
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from pathlib import Path
import orjson

# Import the async watch function
from claude_parser.watch import watch_async, stream_for_sse

app = FastAPI()


# ============================================
# 95% Use Case: One-liner SSE endpoint
# ============================================

@app.get("/api/stream/simple")
async def simple_stream():
    """
    Simplest possible SSE endpoint - one line!
    
    This replaces ~500 lines of WebSocket/polling code.
    """
    return EventSourceResponse(
        stream_for_sse("session.jsonl")
    )


# ============================================
# Custom formatting for specific project needs
# ============================================

@app.get("/api/v2/projects/{project_name}/stream")
async def memory_project_stream(project_name: str, session_id: str = None):
    """
    Memory project compatible SSE endpoint.
    
    No threading, no polling, no complexity!
    """
    # Get the JSONL file path for this project
    jsonl_path = Path.home() / ".claude" / "projects" / project_name / "current.jsonl"
    
    async def generate_events():
        """Generate SSE events from file changes."""
        async for conv, new_messages in watch_async(jsonl_path):
            for msg in new_messages:
                # Filter by session if provided
                if session_id and msg.session_id != session_id:
                    continue
                
                # Format for memory project frontend
                event_data = {
                    "id": msg.uuid,
                    "type": msg.type.value,
                    "content": msg.text_content,
                    "role": "assistant" if msg.type.value == "assistant" else "user",
                    "metadata": {
                        "timestamp": msg.timestamp,
                        "session_id": msg.session_id,
                        "project": project_name,
                        "parent_uuid": msg.parent_uuid,
                        # Tool-specific fields
                        "tool_name": getattr(msg, 'tool_name', None),
                        "tool_use_id": getattr(msg, 'tool_use_id', None),
                    }
                }
                
                yield {"data": json.dumps(event_data)}
    
    return EventSourceResponse(generate_events())


# ============================================
# Advanced: With stop control
# ============================================

import asyncio

# Store active connections
active_streams = {}

@app.get("/api/stream/controlled/{session_id}")
async def controlled_stream(session_id: str):
    """
    Stream with ability to stop from another endpoint.
    """
    # Create stop event for this session
    stop_event = asyncio.Event()
    active_streams[session_id] = stop_event
    
    async def generate_with_control():
        try:
            async for conv, new_messages in watch_async(
                f"sessions/{session_id}.jsonl",
                stop_event=stop_event
            ):
                for msg in new_messages:
                    yield {"data": json.dumps({
                        "type": msg.type.value,
                        "content": msg.text_content
                    })}
        finally:
            # Clean up when done
            active_streams.pop(session_id, None)
    
    return EventSourceResponse(generate_with_control())


@app.post("/api/stream/stop/{session_id}")
async def stop_stream(session_id: str):
    """Stop a specific stream."""
    if session_id in active_streams:
        active_streams[session_id].set()
        return {"status": "stopped"}
    return {"status": "not_found"}


# ============================================
# Filter by message type
# ============================================

@app.get("/api/stream/tools")
async def stream_tool_operations():
    """
    Stream only tool-related messages.
    
    Perfect for monitoring tool usage in real-time.
    """
    async def tool_events():
        # Only watch for tool messages
        async for conv, new_messages in watch_async(
            "session.jsonl",
            message_types=["tool_use", "tool_result"]
        ):
            for msg in new_messages:
                event = {
                    "type": msg.type.value,
                    "tool_name": getattr(msg, 'tool_name', None),
                    "tool_use_id": getattr(msg, 'tool_use_id', None),
                    "content": msg.text_content,
                    "timestamp": msg.timestamp
                }
                yield {"data": json.dumps(event)}
    
    return EventSourceResponse(tool_events())


# ============================================
# With heartbeat for connection keep-alive
# ============================================

@app.get("/api/stream/with-heartbeat")
async def stream_with_heartbeat():
    """
    Stream with periodic heartbeats to keep connection alive.
    """
    async def events_with_heartbeat():
        import asyncio
        
        # Create a queue for messages
        queue = asyncio.Queue()
        
        # Start file watching in background
        async def watch_task():
            async for conv, new_messages in watch_async("session.jsonl"):
                for msg in new_messages:
                    await queue.put(msg)
        
        # Start watcher
        asyncio.create_task(watch_task())
        
        # Stream with heartbeats
        while True:
            try:
                # Wait for message with timeout
                msg = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield {"data": json.dumps({
                    "type": msg.type.value,
                    "content": msg.text_content
                })}
            except asyncio.TimeoutError:
                # Send heartbeat if no messages for 30s
                yield {"data": json.dumps({"type": "heartbeat"})}
    
    return EventSourceResponse(events_with_heartbeat())


if __name__ == "__main__":
    import uvicorn
    
    print("""
    🚀 95/5 SSE Streaming Server
    
    No manual threading needed - watchfiles handles it all!
    
    Endpoints:
    - http://localhost:8000/api/stream/simple - Basic streaming
    - http://localhost:8000/api/stream/tools - Tool operations only
    - http://localhost:8000/api/v2/projects/{name}/stream - Memory project format
    
    Test with:
    curl -N http://localhost:8000/api/stream/simple
    """)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)