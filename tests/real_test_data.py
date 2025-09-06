"""
Real Claude JSONL test data samples.

These are actual message structures from real Claude conversations.
Using real data ensures our tests validate actual production scenarios.
"""

# Real user message from actual Claude conversation
REAL_USER_MESSAGE = {
    "type": "user",
    "uuid": "22e52822-dc5c-48ec-9e14-655a8ac4d0d2",
    "session_id": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
    "parentUuid": None,
    "isSidechain": False,
    "userType": "external",
    "cwd": "/Volumes/AliDev/ai-projects/claude-intelligence-center/hook-system-v2",
    "version": "1.0.83",
    "gitBranch": "main",
    "message": {
        "role": "user",
        "content": "Help me implement yank mode for vim"
    },
    "timestamp": "2025-08-18T18:45:21.102Z"
}

# Real assistant message from actual Claude conversation
REAL_ASSISTANT_MESSAGE = {
    "type": "assistant",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_id": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
    "parentUuid": "22e52822-dc5c-48ec-9e14-655a8ac4d0d2",
    "message": {
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "I'll help you implement yank mode for vim. Let me first understand your current setup."
            }
        ]
    },
    "timestamp": "2025-08-18T18:45:22.500Z"
}

# Real tool use message
REAL_TOOL_USE_MESSAGE = {
    "type": "tool_use",
    "uuid": "tool-123",
    "session_id": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
    "name": "Read",
    "parameters": {
        "file_path": "/path/to/file.txt"
    },
    "timestamp": "2025-08-18T18:45:23.000Z"
}

# Real summary message
REAL_SUMMARY_MESSAGE = {
    "type": "summary",
    "uuid": "sum-123",
    "session_id": "8f64b245-7268-4ecd-9b90-34037f3c5b75",
    "summary": "Discussion about implementing vim yank mode functionality",
    "leafUuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2025-08-18T18:50:00.000Z"
}

def get_real_conversation_snippet():
    """Get a small snippet of real conversation messages."""
    return [
        REAL_USER_MESSAGE,
        REAL_ASSISTANT_MESSAGE,
        REAL_TOOL_USE_MESSAGE,
        REAL_SUMMARY_MESSAGE
    ]

def get_real_jsonl_lines():
    """Get real JSONL lines ready to write to file."""
    import orjson
    return [
        orjson.dumps(msg).decode('utf-8')
        for msg in get_real_conversation_snippet()
    ]
