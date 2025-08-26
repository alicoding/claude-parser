#!/usr/bin/env python3
"""Test with actual parse_message."""

import orjson
from claude_parser.models import parse_message

line = """{"parentUuid": "393689ce-925b-46d2-8765-d3ca628b9935", "isSidechain": false, "userType": "external", "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2", "sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75", "version": "1.0.83", "gitBranch": "main", "type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_01Neh8n24ZfgEhBn9BRGwCHY", "type": "tool_result", "content": [{"type": "text", "text": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2/cchooks_platform/monitor_service_celery.py"}]}]}}"""

data = orjson.loads(line)

# Monkey patch to see exception
original_parse = parse_message

def debug_parse(data):
    try:
        return original_parse.__wrapped__(data)  # Call original without wrapper
    except Exception as e:
        print(f"Exception in parse_message: {e}")
        import traceback
        traceback.print_exc()
        raise

# Actually, let's just inline the logic to debug
try:
    msg_type = data.get("type", "")
    messages = []
    
    # Check for embedded tool uses/results in content array
    if msg_type in ["user", "assistant"]:
        msg_data = data.get("message", {})
        content = msg_data.get("content", [])
        
        # If content is a list, check for embedded tool uses/results
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    item_type = item.get("type")
                    print(f"Processing item type: {item_type}")
                    
                    if item_type == "tool_result":
                        # This is where it would create the ToolResult
                        print("Would create ToolResult")
    
    # Always parse the main message
    print(f"Appending main message of type: {msg_type}")
    messages.append("dummy")
    
    # Return single message or list
    if len(messages) == 1:
        print("Returning single message")
    elif len(messages) > 1:
        print(f"Returning list of {len(messages)} messages")
    else:
        print("Would return None (empty messages list)")
        
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
