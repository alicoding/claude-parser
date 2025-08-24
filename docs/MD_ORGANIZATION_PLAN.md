# 📚 Markdown Files Organization Plan

## Current State: 42 .md files in root (chaos!)

## Proposed Organization:

### docs/planning/ - Project planning and phases
- PHASE2_API_DESIGN.md
- PHASE2_API_VALIDATION.md
- PHASE2_FINAL_PLAN.md
- PHASE2_IMPLEMENTATION.md
- PHASE2_PROGRESS.md
- PHASE2_READY.md
- PHASE2_SEQUENTIAL_PLAN.md
- PHASE2_STRICT_PATTERN.md
- PHASE2_TEST_PLAN.md
- phase2_research.md
- PHASE_1_ISSUES_BACKLOG.md
- PHASE_1_TASKS.md
- README_PLANNING.md
- MIGRATION_PLAN.md
- MIGRATION_TO_VOLUMES.md
- CLEANUP_PLAN.md

### docs/backlog/ - Backlog and tracking
- BACKLOG.md
- BACKLOG_PHASE2.md
- NAVIGATION_SDK_BACKLOG.md
- TYPESCRIPT_SDK_BACKLOG.md
- PROGRESS_TRACKER.md
- SESSION_HANDOFF.md
- SESSION_SUMMARY.md

### docs/specifications/ - Technical specifications
- SPECIFICATION.md
- 95_5_PATTERNS.md
- 95_5_violations.md
- APPROVED_LIBRARIES.md
- TARGET_STATE.md
- VIOLATION_FIXES.md
- ZERO_DEBT_CHECKLIST.md
- RESTRUCTURE_ANALYSIS.md

### docs/process/ - Development process docs
- DELIVERY_CONTRACT.md
- RELEASE_PROCESS.md
- GITHUB_CHECKLIST.md
- CCHOOKS_COMPARISON.md

### docs/research/ - Research and analysis
- LIBRARY_RESEARCH_2025.md
- NAVIGATION_LIBRARIES_NEEDED.md
- microcontext.md

### Keep in Root (Important/Required):
- README.md - Main project README (required)
- README_GITHUB.md - GitHub specific (might be needed)
- CHANGELOG.md - Standard location
- CLAUDE.md - AI instructions (needs to be in root)

## Commands to Execute:

```bash
# Create directories
mkdir -p docs/planning
mkdir -p docs/backlog
mkdir -p docs/specifications
mkdir -p docs/process
mkdir -p docs/research

# Move planning docs
mv PHASE2_*.md docs/planning/
mv phase2_research.md docs/planning/
mv PHASE_1_*.md docs/planning/
mv README_PLANNING.md docs/planning/
mv MIGRATION_*.md docs/planning/
mv CLEANUP_PLAN.md docs/planning/

# Move backlog docs
mv BACKLOG*.md docs/backlog/
mv *_BACKLOG.md docs/backlog/
mv PROGRESS_TRACKER.md docs/backlog/
mv SESSION_*.md docs/backlog/

# Move specifications
mv SPECIFICATION.md docs/specifications/
mv 95_5_*.md docs/specifications/
mv APPROVED_LIBRARIES.md docs/specifications/
mv TARGET_STATE.md docs/specifications/
mv VIOLATION_FIXES.md docs/specifications/
mv ZERO_DEBT_CHECKLIST.md docs/specifications/
mv RESTRUCTURE_ANALYSIS.md docs/specifications/

# Move process docs
mv DELIVERY_CONTRACT.md docs/process/
mv RELEASE_PROCESS.md docs/process/
mv GITHUB_CHECKLIST.md docs/process/
mv CCHOOKS_COMPARISON.md docs/process/

# Move research docs
mv LIBRARY_RESEARCH_2025.md docs/research/
mv NAVIGATION_LIBRARIES_NEEDED.md docs/research/
mv microcontext.md docs/research/
```

## Result:
- **Before**: 42 .md files in root
- **After**: 4 .md files in root (only essential ones)
- **Organized**: 38 files into logical categories