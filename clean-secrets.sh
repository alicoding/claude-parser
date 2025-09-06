#!/bin/bash

# Script to remove secrets from git history
# WARNING: This rewrites git history!

echo "⚠️  WARNING: This will rewrite git history!"
echo "Make sure you have:"
echo "1. Rotated the exposed API keys"
echo "2. Backed up your repository"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

# Create a file with secrets to remove
cat > secrets.txt << 'EOF'
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==>REDACTED_OPENAI_KEY
ek-proxy-E4CgKTRcrO7gEyGQz0kLRFDMXeDsRTljxJM2TjVRNDhS==>REDACTED_ELECTRONHUB_KEY
EOF

# Install BFG if not present
if ! command -v bfg &> /dev/null; then
    echo "Installing BFG Repo Cleaner..."
    brew install bfg
fi

# Clean the history
echo "Cleaning git history..."
bfg --replace-text secrets.txt

# Clean up
rm secrets.txt

echo "✅ History cleaned!"
echo ""
echo "Now run:"
echo "  git reflog expire --expire=now --all"
echo "  git gc --prune=now --aggressive"
echo "  git push --force-with-lease"
echo ""
echo "⚠️  IMPORTANT: All collaborators need to re-clone the repository!"
