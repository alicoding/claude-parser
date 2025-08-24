#!/usr/bin/env python3
"""Debug parse_message."""

import orjson
from claude_parser.models import parse_message, UserMessage, ToolResult, MessageType

line = """{"parentUuid": "393689ce-925b-46d2-8765-d3ca628b9935", "isSidechain": false, "userType": "external", "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2", "sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75", "version": "1.0.83", "gitBranch": "main", "type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_01Neh8n24ZfgEhBn9BRGwCHY", "type": "tool_result", "content": [{"type": "text", "text": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2/cchooks_platform/monitor_service_celery.py"}]}]}}"""

data = orjson.loads(line)

# Try parsing directly
try:
    msg_type = data.get("type", "")
    print(f"Message type: {msg_type}")
    
    if msg_type == "user":
        # Check content
        msg_data = data.get("message", {})
        content = msg_data.get("content", [])
        print(f"Content type: {type(content)}")
        print(f"Content length: {len(content) if isinstance(content, list) else 'N/A'}")
        
        if isinstance(content, list):
            for i, item in enumerate(content):
                if isinstance(item, dict):
                    print(f"Item {i}: type={item.get('type')}")
                    
                    # Check for tool_result  
                    if item.get("type") == "tool_result":
                        print(f"  Found tool_result with id: {item.get('tool_use_id')}")
                        # The content is nested AGAIN
                        inner_content = item.get("content", [])
                        print(f"  Inner content type: {type(inner_content)}")
                        if isinstance(inner_content, list):
                            print(f"  Inner content: {inner_content}")
        
        # Try creating the message
        user_msg = UserMessage(**data)
        print(f"Created UserMessage: {user_msg.type}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()