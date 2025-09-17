#!/usr/bin/env python3
"""
Discover actual JSONL structure using real data
@TDD_REAL_DATA: Uses production JSONL
@FRAMEWORK_FIRST: Uses DuckDB for analysis
"""

import json
import duckdb
from pathlib import Path
from genson import SchemaBuilder

# Real JSONL path from memory map
jsonl_path = Path("/Volumes/AliDev/ai-projects/claude-parser/jsonl-prod-data-for-test/-Volumes-AliDev-ai-projects-claude-parser/3a7770b4-aba3-46dd-b677-8fc2d71d4e06.jsonl")

print("=== ANALYZING REAL JSONL STRUCTURE ===\n")

# Method 1: Use DuckDB to read JSONL
conn = duckdb.connect()
df = conn.execute(f"SELECT * FROM read_json_auto('{jsonl_path}')").df()
print(f"Total rows in JSONL: {len(df)}")
print(f"Columns: {list(df.columns)}\n")

# Method 2: Use Genson to discover schema
builder = SchemaBuilder()
messages = []
with open(jsonl_path, 'r') as f:
    for line in f:
        msg = json.loads(line)
        messages.append(msg)
        builder.add_object(msg)

schema = builder.to_schema()

print("=== MESSAGE TYPES FOUND ===")
message_types = {}
for msg in messages:
    msg_type = msg.get('type', 'unknown')
    if msg_type not in message_types:
        message_types[msg_type] = 0
    message_types[msg_type] += 1

for msg_type, count in message_types.items():
    print(f"  {msg_type}: {count}")

print("\n=== SAMPLE USER MESSAGE ===")
for msg in messages:
    if msg.get('type') == 'user':
        print(json.dumps(msg, indent=2)[:1000])
        break

print("\n=== SAMPLE ASSISTANT MESSAGE ===")
for msg in messages:
    if msg.get('type') == 'assistant':
        # Check the structure
        if 'message' in msg and msg['message']:
            print(f"Has 'message' field with keys: {list(msg['message'].keys())}")
            if 'content' in msg['message']:
                content = msg['message']['content']
                print(f"message.content type: {type(content)}")
                if isinstance(content, str):
                    print(f"message.content preview: {content[:200]}")
        print(json.dumps(msg, indent=2)[:1000])
        break