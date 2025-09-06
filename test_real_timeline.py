#!/usr/bin/env python3
"""
Test the new RealClaudeTimeline with authentic Claude Code JSONL data.
"""

from pathlib import Path
from claude_parser.domain.services.real_claude_timeline import RealClaudeTimeline

def test_real_timeline():
    """Test timeline with real Claude Code data from /tmp/claude-parser-test-project."""

    # Use our real test project
    test_project_path = Path("/tmp/claude-parser-test-project")

    print(f"🔍 Testing RealClaudeTimeline with {test_project_path}")

    try:
        # Initialize timeline - should auto-discover JSONL files
        timeline = RealClaudeTimeline(test_project_path)

        print(f"✅ Timeline initialized successfully")
        print(f"📊 Found {len(timeline.tool_operations)} tool operations")
        print(f"📁 Raw events: {len(timeline.raw_events)}")

        # Test multi-session summary
        summary = timeline.get_multi_session_summary()
        print(f"\n📈 Multi-Session Summary:")
        print(f"   Sessions: {summary['total_sessions']}")
        print(f"   Operations: {summary['total_operations']}")

        for session_id, data in summary['sessions'].items():
            short_id = session_id[:8] if session_id != "unknown" else session_id
            print(f"   📋 Session {short_id}: {data['operations']} ops, files: {data['files_modified']}")

        # Test checkout latest
        latest_state = timeline.checkout("latest")
        print(f"\n📄 Latest state: {list(latest_state.keys())}")

        # Test UUID navigation with Edit operations (not Read)
        edit_operations = [op for op in timeline.tool_operations
                          if op.get("tool_name") in ["Write", "Edit", "MultiEdit"]]

        if edit_operations:
            first_edit_uuid = edit_operations[0].get("uuid")
            if first_edit_uuid:
                print(f"\n🔄 Testing UUID checkout: {first_edit_uuid[:8]}...")
                uuid_state = timeline.checkout_by_uuid(first_edit_uuid)
                if uuid_state:
                    print(f"✅ UUID checkout successful: {list(uuid_state.keys())}")
                else:
                    print(f"❌ UUID checkout failed")
        else:
            print(f"\n⚠️ No Edit operations found for UUID testing")

        # Show UUID mapping
        print(f"\n🗂️ UUID to Commit mapping: {len(timeline._uuid_to_commit)} entries")
        for uuid, commit in list(timeline._uuid_to_commit.items())[:3]:
            print(f"   {uuid[:8]} → {commit[:8]}")

        # Clean up
        timeline.clear_cache()
        print(f"\n✅ Test completed successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_timeline()
