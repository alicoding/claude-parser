#!/bin/bash
# Prepare for PyPI release

set -e

echo "🚀 Preparing Claude Parser for Release"
echo "======================================="

# Check if we're on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo "❌ Must be on main branch to release (currently on $BRANCH)"
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet; then
    echo "❌ Uncommitted changes detected. Commit or stash them first."
    exit 1
fi

# Get current version
CURRENT_VERSION=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Current version: $CURRENT_VERSION"

# Prompt for new version
echo "Enter new version (or press Enter to keep $CURRENT_VERSION):"
read NEW_VERSION

if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
else
    # Update version in pyproject.toml
    sed -i.bak "s/version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    rm pyproject.toml.bak
    echo "✅ Updated version to $NEW_VERSION"
fi

# Run quality checks
echo ""
echo "🔍 Running quality checks..."
echo "----------------------------"

# Run tests
echo "Running tests..."
poetry run pytest tests/ --cov=claude_parser --cov-fail-under=80

# Run linting
echo "Running linting..."
poetry run ruff check claude_parser tests

# Build package
echo ""
echo "📦 Building package..."
poetry build

# Check the build
echo ""
echo "🔍 Checking package..."
pip install twine
twine check dist/*

echo ""
echo "✅ Release preparation complete!"
echo ""
echo "Next steps:"
echo "1. Review changes: git diff"
echo "2. Commit: git add -A && git commit -m 'chore: release v$NEW_VERSION'"
echo "3. Tag: git tag v$NEW_VERSION"
echo "4. Push: git push && git push --tags"
echo "5. Create GitHub release at https://github.com/anthropics/claude-parser/releases"
echo ""
echo "The GitHub Action will automatically publish to PyPI when the release is created."