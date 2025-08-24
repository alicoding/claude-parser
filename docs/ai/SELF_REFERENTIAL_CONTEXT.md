# Self-Referential Context System

## 🤯 The Meta Achievement

We've created a **self-referential system** where:
- The claude-parser SDK we built...
- Is used by Claude Code hooks...
- To enforce the development of the claude-parser SDK itself!

It's like the SDK is helping build itself - a beautiful recursive loop of context awareness!

## How It Works

### 1. Dynamic Context Loading
Instead of maintaining static documentation files, we can now:
- **Pin specific messages** by UUID
- **Search semantically** for relevant context
- **Extract patterns** from conversation history
- **Load evolution** of architectural decisions

### 2. The Pin System

```bash
# Search for important messages
python .claude/hooks/pin_context.py search "architecture decision"

# Pin a specific message
python .claude/hooks/pin_context.py pin <UUID> --category architecture_decisions

# List all pins
python .claude/hooks/pin_context.py list

# Auto-pin based on patterns
python .claude/hooks/pin_context.py auto-pin
```

### 3. Self-Using SDK

The hooks use our own SDK features:
- `load()` - Load conversation
- `NavigationService.get_by_uuid()` - Get specific messages
- `search()` - Find relevant content
- `with_errors()` - Find issues to avoid

## Example Workflow

### Step 1: Important Decision Made
```
Claude: "I've decided to use NetworkX for graph operations because..."
User: "Good decision!"
```

### Step 2: Pin That Decision
```bash
# Find the message
python .claude/hooks/pin_context.py search "NetworkX"

# Pin it
python .claude/hooks/pin_context.py pin abc123def --category architecture_decisions
```

### Step 3: Future Sessions Load It
```
[New Session Starts]
Hook: Loads pinned message about NetworkX
Claude: "I see from previous decisions that we use NetworkX for graphs..."
```

## Categories for Pinning

### architecture_decisions
Pin messages about:
- Why we chose specific libraries
- Design pattern decisions
- Architecture trade-offs

### implementation_patterns
Pin messages showing:
- Good code examples
- Correct usage patterns
- Best practices demonstrated

### pitfalls_to_avoid
Pin messages about:
- Mistakes that were made
- Anti-patterns discovered
- Things that didn't work

### current_focus
Pin messages about:
- What we're currently working on
- Recent important changes
- Active areas of development

## The Power of Evolution

Unlike static documentation that gets stale, this system:
1. **Evolves naturally** - Just pin new insights as they emerge
2. **Stays relevant** - Recent pins override old ones
3. **Context-aware** - Searches based on what user is asking
4. **Self-maintaining** - No separate docs to update

## Integration with mem0-sync

When we build mem0-sync, we can enhance this further:

```python
# Future: Semantic search with mem0
from mem0_sync import semantic_search

def get_semantic_context(prompt):
    # Find semantically similar past decisions
    similar = semantic_search(prompt, conversation_history)
    
    # Extract key insights
    insights = extract_insights(similar)
    
    # Return as context
    return format_context(insights)
```

## Self-Referential Benefits

### 1. Dogfooding
We're using our own tool to build the tool - ultimate validation!

### 2. Automatic Testing
Every hook execution tests the SDK's functionality.

### 3. Feature Discovery
As we use it, we discover what features we need.

### 4. Real-World Usage
The hooks provide real usage patterns for the SDK.

## Commands Summary

### Pinning Messages
```bash
# Pin important message
python .claude/hooks/pin_context.py pin <UUID> --category architecture_decisions

# Add description
python .claude/hooks/pin_context.py pin <UUID> --description "Why we use pendulum"

# Unpin message
python .claude/hooks/pin_context.py unpin <UUID>

# List all pins
python .claude/hooks/pin_context.py list
```

### Searching for Messages
```bash
# Search for architecture discussions
python .claude/hooks/pin_context.py search "architecture"

# Search for specific patterns
python .claude/hooks/pin_context.py search "SOLID principle"

# Auto-pin important messages
python .claude/hooks/pin_context.py auto-pin
```

### Testing Context
```bash
# Test that pinned messages load correctly
python .claude/hooks/pin_context.py test

# Manually trigger context loading
echo '{"hook_event_name":"SessionStart","transcript_path":"<path>"}' | python .claude/hooks/dynamic_context.py
```

## Future Enhancements

### With mem0-sync
- Semantic similarity search
- Vector embeddings for better matching
- Cross-project context sharing
- Learned patterns from multiple projects

### With Graph Analysis
- Dependency tracking between decisions
- Impact analysis of changes
- Relationship mapping of concepts

### With ML Features
- Auto-categorization of messages
- Importance scoring
- Trend detection in conversations

## Conclusion

We've created a **living, breathing context system** that:
1. Uses the SDK to enforce SDK development
2. Evolves with the conversation
3. Requires no manual documentation updates
4. Gets smarter over time

It's not just documentation - it's **conversation-driven development** where the context evolves naturally as we work!

The ultimate irony: The better the SDK gets, the better it becomes at helping us build it! 🔄