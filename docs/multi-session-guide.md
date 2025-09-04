# Multi-Session Guide 🔀

> **Understanding and managing concurrent Claude Code sessions on the same project**

When multiple Claude Code sessions work on the same project (either sequentially or concurrently), claude-parser automatically tracks and aggregates all operations to give you complete visibility and control.

## 🧠 Understanding Multi-Session Scenarios

### What Are Sessions?
Each time you start Claude Code, it creates a new session with a unique ID (UUID). Even if you're working on the same project, different conversations/terminals/timeframes create separate sessions.

### Common Multi-Session Scenarios

#### 1. **Sequential Work Sessions**
```bash
# Morning session - you work with Claude on app.py
claude "Add user authentication to app.py"  # Session: abc12345

# Afternoon session - you continue work
claude "Add password validation to app.py" # Session: def67890

# Both sessions modified app.py - how do you track changes?
```

#### 2. **Concurrent Development**
```bash
# Terminal 1: Working on frontend
claude "Update the React components"        # Session: ghi34567

# Terminal 2: Working on backend (at same time)
claude "Add API endpoints"                  # Session: jkl78901

# Both sessions modify overlapping files
```

#### 3. **Experimental Branches**
```bash
# Main development
claude "Implement feature X"               # Session: mno45678

# Trying different approach
claude "Try alternative implementation"    # Session: pqr90123

# Want to compare or merge approaches
```

#### 4. **Team Collaboration**
```bash
# Developer A uses Claude
claude "Refactor database layer"           # Session: stu56789

# Developer B also uses Claude on same project
claude "Add error handling"               # Session: vwx01234

# Project now has changes from both Claude sessions
```

## 🔍 Detecting Multi-Session Situations

### Quick Check: Are Multiple Sessions Present?

```bash
cd /your/project
cg status --sessions
```

**Single Session Output:**
```
📊 Multi-Session Summary
   Sessions: 1
   Operations: 8
   📋 Session abc12345: 8 ops → app.py, config.py
```

**Multi-Session Output:**
```
📊 Multi-Session Summary
   Sessions: 3
   Operations: 24
   📋 Session abc12345: 8 ops → app.py, config.py
   📋 Session def67890: 10 ops → utils.py, app.py
   📋 Session ghi34567: 6 ops → tests.py
```

### Session Timeline Analysis

```bash
# See operations chronologically across all sessions
cg log --file app.py
```

**Multi-Session Timeline:**
```
📅 Timeline for app.py (12 operations)
   1. a1b2c3d4 (Write) [abc12345] 2025-01-04T09:15:30
   2. e5f6g7h8 (Edit) [abc12345] 2025-01-04T09:16:45
   3. i9j0k1l2 (Edit) [def67890] 2025-01-04T14:17:20  ← Different session
   4. m3n4o5p6 (MultiEdit) [abc12345] 2025-01-04T09:18:10
   5. q7r8s9t0 (Edit) [def67890] 2025-01-04T14:19:30  ← Different session
   6. u1v2w3x4 (Edit) [ghi34567] 2025-01-04T16:20:45  ← Third session!
```

Notice:
- **Session IDs** in brackets `[abc12345]` show which session made each change
- **Timestamps** show when operations happened (may not be sequential)
- **Operations are chronologically ordered** regardless of session

## 🎯 Multi-Session Workflows

### Scenario 1: "What Changed Since My Last Session?"

You worked with Claude this morning, then worked again this afternoon. What changed?

```bash
# Check for multiple sessions
cg status --sessions
# Shows: Sessions: 2

# See all changes chronologically
cg log --limit 10
# Shows recent operations from both sessions

# Find where your morning session ended
cg log --session abc12345
# Shows only morning session operations

# See what afternoon session added
cg log --session def67890
# Shows only afternoon session operations
```

### Scenario 2: "File Conflict Resolution"

Two sessions modified the same file differently:

```bash
# See the conflict timeline
cg log --file config.py
# 📅 Timeline for config.py (6 operations)
#    1. a1b2c3d4 (Write) [abc12345] 2025-01-04T09:00:00   ← Session A
#    2. e5f6g7h8 (Edit) [abc12345] 2025-01-04T09:01:00    ← Session A
#    3. i9j0k1l2 (Edit) [def67890] 2025-01-04T14:00:00    ← Session B
#    4. m3n4o5p6 (Edit) [abc12345] 2025-01-04T09:02:00    ← Session A (later!)
#    5. q7r8s9t0 (Edit) [def67890] 2025-01-04T14:01:00    ← Session B
#    6. u1v2w3x4 (Edit) [abc12345] 2025-01-04T09:03:00    ← Session A

# Current state has changes from both sessions mixed together
# Go back to before the conflict
cg checkout e5f6g7h8  # Last operation before Session B started

# Or see what each session contributed
cg diff a1b2c3d4..e5f6g7h8  # Session A's changes
cg diff i9j0k1l2..q7r8s9t0  # Session B's changes
```

### Scenario 3: "Undo Across Sessions"

You want to undo the last 5 operations, but they came from different sessions:

```bash
# This just works - undo goes back chronologically
cg undo 5
# ✅ Undid 5 change(s) across multiple sessions
# 📄 Restored: config.py, app.py, utils.py
# 🆔 Back to UUID: a1b2c3d4

# The undo crossed session boundaries automatically
cg log --limit 10
# Shows you're now at an earlier state that spans sessions
```

### Scenario 4: "Session Isolation Testing"

You want to see what your project looked like with only one session's changes:

```bash
# Get list of sessions
cg status --sessions
# 📋 Session abc12345: 8 ops → app.py, config.py
# 📋 Session def67890: 10 ops → utils.py, app.py

# Find where Session A ended (before Session B started)
cg log --session abc12345
# Last operation: u1v2w3x4

# Go to that state
cg checkout u1v2w3x4
# Now you see project with only Session A's changes

# Compare with current (both sessions)
cg checkout HEAD  # Back to latest
cg diff u1v2w3x4..HEAD  # See what Session B added
```

## ⚠️ Multi-Session Challenges & Solutions

### Challenge 1: Overlapping File Changes

**Problem**: Two sessions modify the same lines in a file.

**Solution**: Use timeline view to understand the sequence:
```bash
cg log --file problematic_file.py
# See exact order of changes

cg show <uuid>  # For each operation
# See what each change did

# Go back to known good state
cg checkout <uuid-before-conflict>
```

### Challenge 2: Understanding Session Context

**Problem**: You see an operation but don't remember which session/context it came from.

**Solution**: Session metadata provides context:
```bash
cg show i9j0k1l2
# 🔍 Operation i9j0k1l2
#    Type: Edit
#    File: app.py
#    Session: def67890
#    Timestamp: 2025-01-04T14:17:20
#    Context: This was from your afternoon session

# See all operations from that session
cg log --session def67890
```

### Challenge 3: Incomplete Session Information

**Problem**: Session ended abruptly, unclear what was finished.

**Solution**: Timeline analysis shows completion:
```bash
# Look at session's last operations
cg log --session abc12345 --limit 5
# Shows if session ended mid-task or cleanly

# Check file states at session end
cg log --file important_file.py
# See if session completed work on important files
```

### Challenge 4: Too Many Sessions

**Problem**: Project has many sessions, hard to track.

**Solution**: Focus on recent and relevant sessions:
```bash
# Show only recent operations
cg log --since "yesterday"

# Show only sessions that modified specific files
cg log --file critical_file.py

# Group by session for analysis
cg status --sessions
```

## 🛠️ Advanced Multi-Session Techniques

### Session Branching

Create git branches to isolate session work:

```bash
# Create branch for current session's work
cg branch session-morning-work

# Continue work, then switch to different session approach
cg branch session-afternoon-experiment
cg checkout session-afternoon-experiment

# Compare approaches
cg diff session-morning-work..session-afternoon-experiment

# Merge successful approach
cg checkout main
cg merge session-morning-work
```

### Session Cherry-Picking

Take specific operations from one session:

```bash
# List operations from specific session
cg log --session def67890 --oneline
# Pick the operations you want

# Create branch and apply specific changes
cg branch cherry-pick-session-b
cg checkout e5f6g7h8  # Go to base state
cg apply q7r8s9t0     # Apply specific operation from Session B
```

### Session Diffing

Compare what different sessions contributed:

```bash
# Find session boundaries
cg log --sessions

# Compare session contributions
cg diff --session-diff abc12345..def67890
# Shows what Session B added compared to Session A

# File-specific session comparison
cg diff --session-diff abc12345..def67890 --file app.py
```

## 📊 Multi-Session Best Practices

### 1. **Regular Session Checks**

```bash
# At start of new Claude work
cg status --sessions
# Understand current session landscape

# Before major changes
cg log --limit 5
# See recent activity across sessions
```

### 2. **Session Documentation**

```bash
# Use descriptive branch names for session work
cg branch feature-auth-morning-session
cg branch bugfix-validation-afternoon-session

# Tag important session states
cg tag session-a-complete <uuid>
```

### 3. **Conflict Prevention**

```bash
# Before starting new session work
cg status
# Understand current state

# After session work
cg log --limit 10
# Document what was accomplished
```

### 4. **Recovery Planning**

```bash
# Create recovery points before complex multi-session work
cg tag before-complex-changes <uuid>

# Document session boundaries
cg log --sessions > session-log.txt
```

## 🔍 Debugging Multi-Session Issues

### Issue: "Lost track of changes"

```bash
# Full session timeline
cg log --verbose --sessions

# Per-file analysis
cg log --file <each-important-file>

# Session isolation
for session in $(cg list-sessions); do
  echo "Session $session:"
  cg log --session $session --oneline
done
```

### Issue: "Files in unexpected state"

```bash
# Trace file history across sessions
cg log --file problematic_file.py --verbose

# Compare with known good state
cg checkout <known-good-uuid>
cg diff <known-good-uuid>..HEAD --file problematic_file.py
```

### Issue: "Session operations seem mixed up"

```bash
# Verify chronological order
cg log --format=full
# Check timestamps make sense

# Verify session isolation
cg log --session <session-id> --verbose
# All operations should be from same session
```

## 🎯 Multi-Session Success Stories

### Story 1: Frontend/Backend Parallel Development

**Situation**: Two terminal sessions working simultaneously.

**Solution**:
```bash
# Terminal 1: Frontend work
cg branch frontend-session
# ... Claude works on React components

# Terminal 2: Backend work
cg branch backend-session
# ... Claude works on API endpoints

# Later: Merge both sessions
cg checkout main
cg merge frontend-session
cg merge backend-session
```

### Story 2: Experimental Feature Development

**Situation**: Trying different approaches in different sessions.

**Solution**:
```bash
# Morning: Try approach A
cg branch approach-a-morning
# ... Session abc12345 implements approach A

# Afternoon: Try approach B
cg branch approach-b-afternoon
# ... Session def67890 implements approach B

# Compare and choose
cg diff approach-a-morning..approach-b-afternoon
cg checkout approach-b-afternoon  # Choose better approach
cg merge main
```

### Story 3: Bug Investigation Across Sessions

**Situation**: Bug appeared after multiple sessions, need to find cause.

**Solution**:
```bash
# Identify when bug appeared
cg bisect start
cg bisect bad HEAD
cg bisect good <uuid-before-bug>

# Test each session's contribution
for session in $(cg list-sessions --since="yesterday"); do
  cg checkout --session-end $session
  # Test for bug
  if bug_present; then
    echo "Bug introduced in session $session"
    break
  fi
done
```

## 📚 Summary

Multi-session support in `cg` provides:
- ✅ **Complete visibility** into all Claude Code sessions affecting your project
- ✅ **Chronological operation ordering** regardless of session boundaries
- ✅ **Session-aware navigation** with context preservation
- ✅ **Conflict resolution tools** for overlapping changes
- ✅ **Zero configuration** - automatically detects and handles multiple sessions

The key insight: **You don't need to manage sessions manually**. The `cg` command aggregates everything chronologically and lets you navigate through the complete history as if it were a single timeline, while still providing session context when you need it.
