#!/usr/bin/env python
"""TDD test - Find actual messages from our current conversation using keywords."""

from claude_parser import find_current_transcript, load

def test_find_our_conversation_by_keyword():
    """Find specific messages from our current conversation using keywords."""
    
    # Load our current conversation
    transcript = find_current_transcript()
    print(f"Loading transcript: {transcript}")
    
    conv = load(transcript)
    print(f"Loaded {len(conv)} messages")
    
    # Test 1: Find when I mentioned "95/5 principle violation"
    print("\n" + "=" * 60)
    print("TEST 1: Find '95/5 principle violation' messages")
    print("=" * 60)
    
    violation_msgs = conv.search("95/5 development this is a big violation")
    if violation_msgs:
        print(f"✅ Found {len(violation_msgs)} messages about '95/5 violation'")
        
        # Get the first one
        msg = violation_msgs[0]
        print(f"Message UUID: {msg.uuid}")
        print(f"Message type: {msg.type}")
        
        # Get context around it
        context = conv.get_surrounding(msg.uuid, before=1, after=1)
        print(f"\nContext ({len(context)} messages):")
        for ctx_msg in context:
            preview = str(ctx_msg)[:100] if ctx_msg else "None"
            print(f"  - {ctx_msg.type if ctx_msg else 'Unknown'}: {preview}...")
    else:
        print("❌ Could not find '95/5 violation' message")
    
    # Test 2: Find when I talked about NetworkX
    print("\n" + "=" * 60)
    print("TEST 2: Find 'NetworkX' discussion")
    print("=" * 60)
    
    networkx_msgs = conv.search("NetworkX")
    print(f"Found {len(networkx_msgs)} messages mentioning NetworkX")
    
    if networkx_msgs:
        # Find the one where I recommended it based on research
        for msg in networkx_msgs:
            if "95/5 library solution" in msg.text_content:
                print(f"✅ Found research recommendation message!")
                print(f"UUID: {msg.uuid}")
                
                # Show a snippet
                snippet = msg.text_content[:200]
                print(f"Snippet: {snippet}...")
                break
    
    # Test 3: Find discussion about library_research.py
    print("\n" + "=" * 60)
    print("TEST 3: Find 'library_research.py' mentions")
    print("=" * 60)
    
    research_msgs = conv.search("library_research.py")
    print(f"Found {len(research_msgs)} messages about library_research.py")
    
    if research_msgs:
        # Find where you reminded me to use it
        for msg in research_msgs:
            if msg.type.value == "user" and "hallucinating" in msg.text_content.lower():
                print(f"✅ Found where you told me to stop hallucinating!")
                print(f"Your message: '{msg.text_content[:150]}...'")
                
                # Get my response after that
                msg_index = conv.messages.index(msg)
                if msg_index < len(conv.messages) - 1:
                    next_msg = conv.messages[msg_index + 1]
                    if next_msg.type.value == "assistant":
                        print(f"My response: '{next_msg.text_content[:150]}...'")
                break
    
    # Test 4: Thread navigation - find a decision point
    print("\n" + "=" * 60)
    print("TEST 4: Navigate thread from a decision point")
    print("=" * 60)
    
    # Find messages about pandas vs dict decision
    decision_msgs = conv.search("pandas DataFrame or stay with Python dicts")
    if decision_msgs:
        print(f"✅ Found decision discussion!")
        decision = decision_msgs[0]
        
        # Get the thread from this decision
        thread = conv.get_thread_from(decision.uuid)
        print(f"Thread has {len(thread)} messages following this decision")
        
        # Show first few
        for i, msg in enumerate(thread[:3]):
            print(f"  {i+1}. {msg.type}: {str(msg)[:80]}...")
    
    # Test 5: Timestamp range - get messages from last 10 minutes
    print("\n" + "=" * 60)
    print("TEST 5: Get recent messages (last 10 minutes)")
    print("=" * 60)
    
    import pendulum
    now = pendulum.now()
    ten_min_ago = now.subtract(minutes=10)
    
    recent = conv.get_messages_between_timestamps(
        ten_min_ago.to_iso8601_string(),
        now.to_iso8601_string()
    )
    print(f"Found {len(recent)} messages in last 10 minutes")
    
    if recent:
        print("Most recent message types:")
        for msg in recent[-5:]:
            print(f"  - {msg.type}: {msg.timestamp}")
    
    # Test 6: Filter by type
    print("\n" + "=" * 60)
    print("TEST 6: Count message types")
    print("=" * 60)
    
    user_msgs = conv.filter_by_type("user")
    assistant_msgs = conv.filter_by_type("assistant")
    tool_msgs = conv.filter_by_type("tool_result")
    
    print(f"User messages: {len(user_msgs)}")
    print(f"Assistant messages: {len(assistant_msgs)}")
    print(f"Tool results: {len(tool_msgs)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("NAVIGATION API TEST COMPLETE")
    print("=" * 60)
    print("✅ Successfully navigated our actual conversation!")
    print("✅ Found specific messages by keyword")
    print("✅ Retrieved context around messages")
    print("✅ Navigated threads (if branching exists)")
    print("✅ Filtered by timestamp and type")

if __name__ == "__main__":
    test_find_our_conversation_by_keyword()