#!/bin/bash
# Pre-commit hook for dstask to enforce task quality
# Install: cp this to ~/.dstask/.git/hooks/pre-commit && chmod +x ~/.dstask/.git/hooks/pre-commit

echo "🔍 Validating task quality..."

# Get the latest task that was added/modified
LATEST_TASK=$(git diff --cached --name-only | grep -E "pending/.*\.yml" | head -1)

if [ -z "$LATEST_TASK" ]; then
    # No task changes, allow commit
    exit 0
fi

# Extract task ID from filename
TASK_ID=$(basename "$LATEST_TASK" .yml)

# Check if task has notes
NOTES=$(git show ":$LATEST_TASK" | grep -A 100 "notes:" | grep -v "notes:")

# Validate required fields
ERRORS=()

if ! echo "$NOTES" | grep -q "LIBRARIES:"; then
    ERRORS+=("❌ Missing LIBRARIES section - run: python scripts/research.py")
fi

if ! echo "$NOTES" | grep -q "COMPLEXITY:"; then
    ERRORS+=("❌ Missing COMPLEXITY target - specify A, B, or C")
fi

if ! echo "$NOTES" | grep -q "DUPLICATES:"; then
    ERRORS+=("❌ Missing DUPLICATES check - grep for similar code")
fi

# Check for 95/5 violations
if echo "$NOTES" | grep -q "for .* in" && ! echo "$NOTES" | grep -q "toolz"; then
    ERRORS+=("⚠️  Manual loops mentioned without toolz alternative")
fi

# Report results
if [ ${#ERRORS[@]} -gt 0 ]; then
    echo "❌ Task validation failed:"
    for error in "${ERRORS[@]}"; do
        echo "  $error"
    done
    echo ""
    echo "💡 Fix with: dstask <id> note"
    echo "📚 Research: python scripts/research.py '<description>'"
    exit 1
fi

echo "✅ Task properly documented!"
exit 0
