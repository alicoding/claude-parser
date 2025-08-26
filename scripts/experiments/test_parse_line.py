#!/usr/bin/env python3
"""Test parsing a specific line."""

import orjson
from claude_parser.models import parse_message

# Test line 642
line = """{"parentUuid": "393689ce-925b-46d2-8765-d3ca628b9935", "isSidechain": false, "userType": "external", "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2", "sessionId": "8f64b245-7268-4ecd-9b90-34037f3c5b75", "version": "1.0.83", "gitBranch": "main", "type": "user", "message": {"role": "user", "content": [{"tool_use_id": "toolu_01Neh8n24ZfgEhBn9BRGwCHY", "type": "tool_result", "content": [{"type": "text", "text": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2/cchooks_platform/monitor_service_celery.py"}]}]}}"""

data = orjson.loads(line)
result = parse_message(data)

print(f"Result type: {type(result)}")
if result:
    if isinstance(result, list):
        print(f"Returned list with {len(result)} items")
        for item in result:
            print(f"  - {item.type}: {type(item)}")
    else:
        print(f"Returned single: {result.type}")
else:
    print("Returned None")
