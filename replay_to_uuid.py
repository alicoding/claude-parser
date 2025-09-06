#!/usr/bin/env python3
"""
Timeline replay system - restore all file operations up to a specific UUID.
Uses the native UUID checkpoint system.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_parser.watch.uuid_tracker import UUIDCheckpointReader


def extract_file_operations_up_to_uuid(
    jsonl_files: List[Path], target_uuid: str
) -> List[Dict[str, Any]]:
    """Extract all file operations up to (and including) the target UUID."""
    all_operations = []

    for jsonl_file in jsonl_files:
        print(f"Processing {jsonl_file.name}...")
        reader = UUIDCheckpointReader(jsonl_file)

        # Get all messages up to target UUID
        messages = reader.get_messages_between(start_uuid=None, end_uuid=target_uuid)

        # Extract file operations from assistant messages
        for message in messages:
            if message.get("type") != "assistant":
                continue

            # Check if message content has tool_use
            msg_content = message.get("message", {})
            content_items = msg_content.get("content", [])

            for content_item in content_items:
                if (content_item.get("type") == "tool_use" and
                    content_item.get("name") in ["Write", "Edit", "MultiEdit"]):

                    operation = {
                        "uuid": message.get("uuid"),
                        "sessionId": message.get("sessionId"),
                        "timestamp": message.get("timestamp"),
                        "tool_name": content_item.get("name"),
                        "tool_input": content_item.get("input", {}),
                        "cwd": message.get("cwd", ""),
                    }

                    # Add file_path for compatibility
                    if "file_path" in operation["tool_input"]:
                        operation["file_path"] = operation["tool_input"]["file_path"]

                    # Only include operations on project files
                    if operation.get("file_path") and "/Volumes/AliDev/ai-projects/claude-parser" in operation["file_path"]:
                        all_operations.append(operation)

        # If we found the target UUID in this file, stop processing other files
        # (since we want operations UP TO the target)
        found_target = any(msg.get("uuid") == target_uuid for msg in messages)
        if found_target:
            print(f"Found target UUID in {jsonl_file.name}, stopping here")
            break

    # Sort by timestamp
    all_operations.sort(key=lambda op: op.get("timestamp", ""))
    return all_operations


def apply_file_operations_to_project(operations: List[Dict[str, Any]], project_path: Path):
    """Apply file operations to restore project state."""
    print(f"Applying {len(operations)} file operations...")

    for i, operation in enumerate(operations):
        file_path = operation.get("file_path")
        tool_name = operation.get("tool_name")
        tool_input = operation.get("tool_input", {})

        if not file_path:
            continue

        # Convert absolute path to relative to project
        try:
            rel_path = Path(file_path).relative_to(project_path)
        except ValueError:
            # If path is not relative to project, use the filename
            rel_path = Path(file_path).name

        target_file = project_path / rel_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        if tool_name == "Write":
            content = tool_input.get("content", "")
            target_file.write_text(content)
            print(f"{i+1:3d}. Write {rel_path} ({len(content)} chars)")

        elif tool_name in ("Edit", "MultiEdit"):
            # Read current content (or empty if doesn't exist)
            if target_file.exists():
                text = target_file.read_text()
            else:
                text = ""

            # Apply edits
            if tool_name == "MultiEdit":
                edits = tool_input.get("edits", [])
                for edit in edits:
                    old_str = edit.get("old_string", "")
                    new_str = edit.get("new_string", "")
                    if old_str in text:
                        text = text.replace(old_str, new_str, 1)
            else:
                old_str = tool_input.get("old_string", "")
                new_str = tool_input.get("new_string", "")
                if old_str in text:
                    text = text.replace(old_str, new_str, 1)

            target_file.write_text(text)
            print(f"{i+1:3d}. Edit {rel_path} ({len(text)} chars)")


def main():
    """Main replay function."""
    project_path = Path('/Volumes/AliDev/ai-projects/claude-parser')
    jsonl_dir = Path("/Users/ali/.claude/projects/-Volumes-AliDev-ai-projects-claude-parser")
    target_uuid = 'fb91c0c0-d553-4615-9fa8-a2387279be83'

    print(f"Replaying file operations up to UUID: {target_uuid}")

    # Get all JSONL files, sorted by modification time (chronological)
    jsonl_files = sorted(jsonl_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime)
    print(f"Found {len(jsonl_files)} JSONL files")

    # Extract all file operations up to target UUID
    operations = extract_file_operations_up_to_uuid(jsonl_files, target_uuid)
    print(f"Extracted {len(operations)} file operations")

    if not operations:
        print("No file operations found up to target UUID")
        return

    # Show what we found
    print("\nFile operations to replay:")
    file_counts = {}
    for op in operations:
        file_path = op.get("file_path", "unknown")
        rel_path = Path(file_path).name
        file_counts[rel_path] = file_counts.get(rel_path, 0) + 1

    for file_path, count in sorted(file_counts.items()):
        print(f"  {file_path}: {count} operations")

    # Look for components directory specifically
    components_ops = [op for op in operations if 'components' in op.get("file_path", "").lower()]
    print(f"\nFound {len(components_ops)} operations on components directory:")
    for op in components_ops:
        file_path = Path(op.get("file_path", "")).name
        tool_name = op.get("tool_name", "")
        print(f"  {tool_name} {file_path}")

    # Apply operations to restore state
    print("\nApplying operations...")
    apply_file_operations_to_project(operations, project_path)

    print(f"\n✅ Replay complete! Project restored to state up to UUID: {target_uuid[:8]}...")

    # Verify components directory was restored
    components_dir = project_path / "claude_parser" / "components"
    if components_dir.exists():
        component_files = list(components_dir.glob("*.py"))
        print(f"✅ Components directory restored with {len(component_files)} files:")
        for f in component_files:
            print(f"  - {f.name}")
    else:
        print("❌ Components directory not found - may not have existed at that UUID")


if __name__ == "__main__":
    main()
