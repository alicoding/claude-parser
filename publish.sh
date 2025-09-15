#!/bin/bash
# Super lazy publishing script - just run ./publish.sh

set -e

echo "🚀 Claude Parser Easy Publisher"
echo "================================"

# Check if we're on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
    echo "⚠️  Not on main branch (currently on $BRANCH)"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Current version: $CURRENT_VERSION"

# Ask for new version
read -p "Enter new version (or press Enter to keep $CURRENT_VERSION): " NEW_VERSION
if [ -z "$NEW_VERSION" ]; then
    NEW_VERSION=$CURRENT_VERSION
fi

# Update version if changed
if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
    echo "📝 Updating version to $NEW_VERSION..."
    sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml
    rm pyproject.toml.bak

    # Commit version bump
    git add pyproject.toml
    git commit -m "chore: Bump version to $NEW_VERSION"
fi

# Build
echo "🔨 Building package..."
poetry build

# Create GitHub release (this triggers the publish workflow)
echo "🏷️  Creating GitHub release..."
git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"
git push origin main --tags

# Create release with GitHub CLI
gh release create "v$NEW_VERSION" \
    --title "v$NEW_VERSION" \
    --generate-notes \
    dist/*.whl dist/*.tar.gz

echo "✅ Done! The GitHub Action will now publish to PyPI automatically."
echo "📦 Check status at: https://github.com/alicoding/claude-parser/actions"
echo "🎉 Once published, install with: pip install claude-parser"