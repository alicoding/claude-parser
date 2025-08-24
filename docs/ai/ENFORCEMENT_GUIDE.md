# Claude Code Context Enforcement Guide

## 🎯 The Problem
Every new Claude Code session starts fresh without memory, leading to:
- Duplicate implementations (hallucination)
- Wrong file placement (architectural violations)
- DRY violations (missing similar patterns)
- Reinventing existing functionality

## ✅ The Solution: Multi-Layer Enforcement

### 1. CLAUDE.md Structure (Session Entry Point)

Based on Anthropic's best practices, structure your CLAUDE.md with:

```markdown
# Project Name

## 🚨 MANDATORY FIRST ACTIONS
Before ANY coding, you MUST:
1. Read @docs/ai/AI_CONTEXT.md
2. Check @docs/ai/CAPABILITY_MATRIX.md  
3. Run: python scripts/codebase_inventory.py . --tree

## ⛔ INSTANT FAILURES (BLOCK ALL WORK)
If you violate these, STOP immediately:
- Creating duplicate functionality → Check CAPABILITY_MATRIX.md
- Wrong file placement → Check AI_CONTEXT.md#file-placement-guide
- Not using existing libraries → Check SPECIFICATION.md

## 🔍 VERIFICATION COMMANDS
# Run these BEFORE any implementation:
python scripts/check_inventory_sync.py     # Is inventory current?
python scripts/verify_spec.py              # Any violations?
python scripts/feature_matrix.py show      # What exists?
```

### 2. Guardrail Patterns in CLAUDE.md

Use XML tags and explicit instruction placement:

```markdown
<rules>
- NEVER create new functionality without checking @docs/ai/CAPABILITY_MATRIX.md
- ALWAYS run `python scripts/codebase_inventory.py . --tree` at session start
- MUST read @docs/ai/CODEBASE_INVENTORY.json before implementing
</rules>

<workflow>
1. Check what exists: Read CAPABILITY_MATRIX.md
2. Find correct location: Check AI_CONTEXT.md  
3. Verify no duplication: Search CODEBASE_INVENTORY.json
4. Only then: Implement
</workflow>
```

### 3. Context Priming Techniques

Place critical instructions at the END (better retention):

```markdown
# [Other content...]

## 🚨 CRITICAL REMINDERS (ALWAYS CHECK)
Remember: You have NO memory from previous sessions!
- The codebase has 85 classes, 140 functions
- Everything is already organized in 9 domains
- Check @docs/ai/CODEBASE_INVENTORY.json for what exists
```

### 4. Automated Enforcement Hooks

#### Pre-commit Hook (.pre-commit-config.yaml)
```yaml
- id: verify-ai-awareness
  name: Verify AI Context Current
  entry: bash -c 'python scripts/check_inventory_sync.py && echo "AI context verified"'
  language: system
  always_run: true
```

#### Git Hook Script (.git/hooks/post-merge)
```bash
#!/bin/bash
echo "⚠️  Codebase changed - updating AI context..."
python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json
echo "✅ AI context updated. Claude will see latest structure."
```

### 5. CI/CD Enforcement

GitHub Actions workflow enforces documentation:

```yaml
- name: Validate AI Understanding
  run: |
    # Check CLAUDE.md references AI docs
    grep -q "@docs/ai/AI_CONTEXT.md" CLAUDE.md || exit 1
    grep -q "@docs/ai/CAPABILITY_MATRIX.md" CLAUDE.md || exit 1
    
    # Verify inventory is current
    python scripts/check_inventory_sync.py
```

### 6. Session Initialization Pattern

Add to CLAUDE.md:

```markdown
## 🎬 SESSION START CHECKLIST
When starting ANY session, Claude MUST:
1. Say: "Checking codebase inventory..."
2. Run: `python scripts/codebase_inventory.py . --stats`
3. Say: "Found X classes, Y functions in Z domains"
4. Only then proceed with the task
```

### 7. Prompt Engineering for Users

Train users to start sessions with:

```
"First, check what exists in the codebase by reading @docs/ai/CAPABILITY_MATRIX.md"
```

Or even better, create an alias:

```bash
alias claude-start="echo 'Check @docs/ai/CAPABILITY_MATRIX.md first' | pbcopy"
```

## 📋 Complete Enforcement Checklist

### Local Enforcement
- [ ] CLAUDE.md has @docs/ai/ references at TOP
- [ ] Pre-commit hooks check inventory sync
- [ ] Post-merge hook auto-updates inventory
- [ ] verify_spec.py includes AI context checks

### Remote Enforcement  
- [ ] GitHub Actions validate on every PR
- [ ] CI blocks merge if inventory outdated
- [ ] PR template includes "Updated AI docs?" checkbox

### Session Enforcement
- [ ] CLAUDE.md has mandatory first actions
- [ ] XML/Markdown tags for guardrails
- [ ] Critical reminders at END of file
- [ ] Session start checklist

### Documentation Enforcement
- [ ] AI_CONTEXT.md is comprehensive
- [ ] CAPABILITY_MATRIX.md lists all features
- [ ] CODEBASE_INVENTORY.json is auto-generated
- [ ] All use hierarchical JSON structure

## 🔑 Key Success Factors

1. **Multiple Touchpoints**: Don't rely on one method
2. **Automation**: Hooks and CI/CD catch human errors
3. **Explicit Over Implicit**: Tell Claude exactly what to check
4. **Fail Fast**: Block work if context not loaded
5. **User Training**: Teach users the right prompts

## 📊 Metrics of Success

Track these in your project:
- Duplicate implementations per month: Should be 0
- Wrong file placements per month: Should be 0  
- Time to first code in session: Should increase (checking first)
- AI context file staleness: Should be <1 day

## 🚀 Implementation Priority

1. **Immediate**: Update CLAUDE.md with mandatory checks
2. **Today**: Add pre-commit hooks
3. **This Week**: Setup CI/CD validation
4. **Ongoing**: Train team on proper prompts

## Example: Enforced CLAUDE.md Opening

```markdown
# Claude Parser SDK

<system-critical>
YOU HAVE NO MEMORY FROM PREVIOUS SESSIONS!
This codebase has 85 classes, 140 functions across 9 domains.
DO NOT CREATE NEW CODE WITHOUT CHECKING WHAT EXISTS.
</system-critical>

## ⛔ BEFORE ANY CODE - MANDATORY
```python
# RUN THIS FIRST - NO EXCEPTIONS
import subprocess
result = subprocess.run(['python', 'scripts/codebase_inventory.py', '.', '--stats'], capture_output=True, text=True)
print(result.stdout)
print("✅ Now I know what exists in the codebase")
```

@docs/ai/AI_CONTEXT.md - START HERE
@docs/ai/CAPABILITY_MATRIX.md - What already exists  
@docs/ai/CODEBASE_INVENTORY.json - Complete structure
```

---

Remember: **Context engineering is about redundancy**. No single method is foolproof, but multiple layers create a robust system that ensures Claude Code always knows what exists before creating anything new.