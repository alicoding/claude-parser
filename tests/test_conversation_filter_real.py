#!/usr/bin/env python3
"""
Test what filter_pure_conversation actually returns with real JSONL
@TDD_REAL_DATA: Production JSONL structure
"""

import json
from pathlib import Path
from claude_parser import load_session
from claude_parser.filtering import filter_pure_conversation

jsonl_path = "/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl"

# Load session
session = load_session(jsonl_path)
messages = session.get('messages', [])

print(f"Total messages: {len(messages)}")

# Get pure conversation
clean = list(filter_pure_conversation(messages))
print(f"After filtering: {len(clean)}")

print("\n=== FIRST USER MESSAGE ===")
for msg in clean:
    if msg.get('type') == 'user' or msg.get('role') == 'user':
        # Show structure
        print(f"Keys: {list(msg.keys())}")

        # Check message field
        if 'message' in msg:
            print(f"message.keys: {list(msg['message'].keys())}")
            content = msg['message'].get('content')
            print(f"Content type: {type(content)}")
            print(f"Content: {content[:200] if isinstance(content, str) else content}")
        break

print("\n=== FIRST ASSISTANT MESSAGE ===")
for msg in clean:
    if msg.get('type') == 'assistant' or msg.get('role') == 'assistant':
        print(f"Keys: {list(msg.keys())}")

        if 'message' in msg:
            print(f"message.keys: {list(msg['message'].keys())}")
            content = msg['message'].get('content')
            print(f"Content type: {type(content)}")

            # Assistant content is a list of blocks
            if isinstance(content, list) and content:
                print(f"First block: {content[0]}")
        break

print("\n=== FOR LLAMAINDEX ===")
print("Each message has:")
print("- type: 'user' or 'assistant'")
print("- message.content: string for user, list of blocks for assistant")
print("- uuid: unique identifier")
print("- timestamp: when message was sent")