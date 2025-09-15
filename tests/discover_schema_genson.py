#!/usr/bin/env python3
"""
Discover ALL fields in Claude JSONL using genson - 100% framework delegation
"""

from genson import SchemaBuilder
import json


def discover_claude_jsonl_schema():
    """Use genson to automatically discover all fields and types in JSONL"""
    
    # Real Claude JSONL file
    jsonl_file = "/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser/0396f326-33fb-4c79-ad54-2494b6278167.jsonl"
    
    print(f"Analyzing: {jsonl_file}\n")
    
    # 100% genson delegation - it discovers EVERYTHING
    builder = SchemaBuilder()
    
    with open(jsonl_file, 'r') as f:
        for line in f:
            obj = json.loads(line)
            builder.add_object(obj)
    
    # Get complete schema with all fields and types
    schema = builder.to_schema()
    
    print("=== COMPLETE SCHEMA DISCOVERED ===\n")
    print(json.dumps(schema, indent=2))
    
    # Find token-related fields
    print("\n=== TOKEN FIELDS ANALYSIS ===\n")
    
    # Check if usage field exists in schema
    if 'properties' in schema:
        props = schema['properties']
        
        # Direct usage field
        if 'usage' in props:
            print("✓ Found 'usage' field:")
            print(json.dumps(props['usage'], indent=2))
        
        # Message.usage field
        if 'message' in props and 'properties' in props['message']:
            if 'usage' in props['message']['properties']:
                print("\n✓ Found 'message.usage' field:")
                print(json.dumps(props['message']['properties']['usage'], indent=2))
        
        # Compact summary field
        if 'isCompactSummary' in props:
            print("\n✓ Found 'isCompactSummary' field:")
            print(json.dumps(props['isCompactSummary'], indent=2))
        
        # Summary field
        if 'summary' in props:
            print("\n✓ Found 'summary' field:")
            print(json.dumps(props['summary'], indent=2))
    
    return schema


if __name__ == "__main__":
    # Discover full schema with genson
    schema = discover_claude_jsonl_schema()
    
    # Summary
    print("\n=== SUMMARY ===")
    if 'properties' in schema:
        print(f"Total fields discovered: {len(schema['properties'])}")
        print(f"Field names: {', '.join(schema['properties'].keys())}")