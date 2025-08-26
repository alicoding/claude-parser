#!/usr/bin/env python
"""TDD-style test to understand Claude's directory structure."""

from pathlib import Path
import orjson

def test_understand_claude_structure():
    """Understand how Claude encodes project paths."""
    
    claude_projects = Path.home() / ".claude" / "projects"
    
    # Test case 1: Check actual cwd values in JSONL files
    print("=" * 60)
    print("TEST: Understanding Claude's directory encoding")
    print("=" * 60)
    
    test_cases = [
        {
            "encoded": "-Volumes-AliDev-ai-projects-claude-intelligence-center-hook-system-v2",
            "expected": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2"
        },
        {
            "encoded": "-Volumes-AliDev-ai-projects-memory",
            "expected": "/Volumes/AliDev/ai-projects/memory"
        },
        {
            "encoded": "-Volumes-AliDev-ai-projects-claude-intelligence-center",
            "expected": "/Volumes/AliDev/ai-projects/claude-intelligence-center"
        }
    ]
    
    for test in test_cases:
        project_dir = claude_projects / test["encoded"]
        print(f"\nDirectory: {test['encoded']}")
        print(f"Expected:  {test['expected']}")
        
        if project_dir.exists():
            # Get first JSONL file
            jsonl_files = list(project_dir.glob("*.jsonl"))
            if jsonl_files:
                # Read multiple lines to find one with cwd
                with open(jsonl_files[0], 'rb') as f:
                    for i, line in enumerate(f):
                        if i >= 10:  # Check first 10 lines
                            break
                        try:
                            data = orjson.loads(line)
                            if 'cwd' in data and data['cwd']:
                                print(f"Actual cwd (line {i+1}): {data['cwd']}")
                                
                                # Test if it matches or is under expected
                                actual_path = Path(data['cwd'])
                                expected_path = Path(test['expected'])
                                
                                if actual_path == expected_path:
                                    print("  ✅ EXACT MATCH")
                                elif actual_path.is_relative_to(expected_path):
                                    print(f"  ✅ CHILD PATH: {actual_path.relative_to(expected_path)}")
                                else:
                                    print(f"  ❌ MISMATCH")
                                break
                        except:
                            continue
            else:
                print("  ⚠️ No JSONL files found")
        else:
            print("  ⚠️ Directory doesn't exist")
    
    print("\n" + "=" * 60)
    print("TEST: Check all projects and their actual paths")
    print("=" * 60)
    
    # List all projects and their actual cwd values
    for project_dir in sorted(claude_projects.iterdir())[:5]:  # First 5 only
        if not project_dir.is_dir():
            continue
            
        print(f"\nDirectory: {project_dir.name}")
        
        jsonl_files = list(project_dir.glob("*.jsonl"))
        if jsonl_files:
            cwds_found = set()
            with open(jsonl_files[0], 'rb') as f:
                for i, line in enumerate(f):
                    if i >= 20:  # Check first 20 lines
                        break
                    try:
                        data = orjson.loads(line)
                        if 'cwd' in data and data['cwd']:
                            cwds_found.add(data['cwd'])
                    except:
                        continue
            
            if cwds_found:
                print("  CWDs found:")
                for cwd in sorted(cwds_found):
                    print(f"    - {cwd}")
            else:
                print("  No cwd fields found in first 20 lines")

if __name__ == "__main__":
    test_understand_claude_structure()
