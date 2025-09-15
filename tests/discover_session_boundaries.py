#!/usr/bin/env python3
"""
Use genson to discover session boundary markers in JSONL
"""

from genson import SchemaBuilder
import json


def discover_session_markers():
    """Discover what fields mark session boundaries"""
    
    jsonl_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser/0396f326-33fb-4c79-ad54-2494b6278167.jsonl"
    
    # Analyze first and last messages to find patterns
    print("=== DISCOVERING SESSION MARKERS ===\n")
    
    with open(jsonl_file, 'r') as f:
        lines = f.readlines()
        
    # Check first 5 messages
    print("FIRST 5 MESSAGES:")
    for i, line in enumerate(lines[:5]):
        msg = json.loads(line)
        print(f"\nMessage {i}:")
        print(f"  type: {msg.get('type')}")
        print(f"  summary: {msg.get('summary', 'N/A')}")
        print(f"  isCompactSummary: {msg.get('isCompactSummary', 'N/A')}")
        print(f"  compactMetadata: {msg.get('compactMetadata', 'N/A')}")
        
        # Check for session continuation in content
        if 'message' in msg and isinstance(msg['message'], dict):
            content = msg['message'].get('content', '')
            if isinstance(content, list) and len(content) > 0:
                first_content = content[0]
                if isinstance(first_content, dict):
                    text = first_content.get('text', '')[:100]
                    if text:
                        print(f"  content preview: {text}...")
    
    # Find compact summaries
    print("\n\n=== SEARCHING FOR COMPACT SUMMARIES ===\n")
    compact_count = 0
    for i, line in enumerate(lines):
        msg = json.loads(line)
        if msg.get('isCompactSummary'):
            compact_count += 1
            print(f"Found compact at line {i}:")
            print(f"  UUID: {msg.get('uuid')}")
            print(f"  compactMetadata: {msg.get('compactMetadata')}")
            if compact_count >= 3:  # Show first 3
                break
    
    # Find summaries
    print("\n\n=== SEARCHING FOR SUMMARIES ===\n")
    summary_count = 0
    for i, line in enumerate(lines):
        msg = json.loads(line)
        if msg.get('type') == 'summary':
            summary_count += 1
            print(f"Found summary at line {i}:")
            print(f"  Summary: {msg.get('summary', 'N/A')[:100]}...")
            print(f"  leafUuid: {msg.get('leafUuid')}")
            if summary_count >= 3:  # Show first 3
                break
    
    print(f"\n\nTotal compact summaries: {compact_count}")
    print(f"Total summaries: {summary_count}")
    
    # Use genson to find boundary patterns
    builder = SchemaBuilder()
    for line in lines[:100]:  # Sample first 100 for schema
        msg = json.loads(line)
        if msg.get('type') == 'summary' or msg.get('isCompactSummary'):
            builder.add_object(msg)


if __name__ == "__main__":
    discover_session_markers()