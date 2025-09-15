# claude-parser Service Catalog
Auto-generated: 2025-09-11 - Prevents wheel reinvention across Claude Code sessions

## 🔌 Core APIs (Direct Import)
```python
from claude_parser import (
    # Session Loading
    load_session, load_latest_session, discover_all_sessions,
    
    # Analytics  
    analyze_session, analyze_project_contexts, analyze_tool_usage,
    
    # Discovery
    discover_claude_files, group_by_projects, analyze_project_structure,
    
    # File Operations
    restore_file_content, generate_file_diff, compare_files, backup_file,
    
    # Timeline Navigation
    find_message_by_uuid, get_message_sequence, get_timeline_summary,
    
    # Token Analysis
    count_tokens, analyze_token_usage, estimate_cost,
    
    # Utilities
    load_many, find_current_transcript, MessageType
)
```

## 💬 Message Utilities
```python
# NEW: Clean text extraction (v2.0.1)
session = load_latest_session()
for msg in session.messages:
    text = msg.get_text()  # ✅ One-liner - no Glom imports needed
```

## 🖥️ CLI Commands
```bash
# Git-like interface
python -m claude_parser.cg_cli status   # Show session status
python -m claude_parser.cg_cli log      # Message history  
python -m claude_parser.cg_cli diff     # Changes between states
```

## 🔧 Advanced APIs
```python
# Session Management
from claude_parser.session import SessionManager
manager = SessionManager()

# Timeline Operations  
from claude_parser.timeline import find_current_checkpoint

# Hooks Integration
from claude_parser.hooks import conversation_enhancer
```

## 📊 Data Structures
```python
# RichMessage - Full metadata access
message.uuid, message.type, message.timestamp
message.get_text()  # ✅ Clean text extraction
message.tool_use_id, message.is_meta

# RichSession - Session container
session.messages, session.session_id, session.metadata
len(session)  # Message count
```

## 🎯 Use Cases Covered
- **Session Loading**: `load_latest_session()` for current conversation  
- **Text Extraction**: `message.get_text()` for Discord/external display
- **File Operations**: Diff/restore for Git-like commands
- **Analytics**: Token counting, tool usage analysis
- **Discovery**: Project file finding, session grouping
- **Timeline**: Message navigation, checkpoint detection

## 🚫 What NOT to Import
- ❌ `glom` - Use `message.get_text()` instead
- ❌ Internal modules - Use public API only
- ❌ `pandas`/`polars` - Use analytics functions

**For lnca-hooks:** Use `message.get_text()` instead of manual content parsing!