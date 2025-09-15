#!/bin/bash
# Development Environment Setup Script
# Ensures all related packages are installed in editable mode
# This prevents import errors during active development

set -e  # Exit on error

echo "Setting up development environment for interdependent packages..."

# Define project root directories
CLAUDE_PARSER_DIR="/Volumes/AliDev/ai-projects/claude-parser"
LNCA_HOOKS_DIR="/Volumes/AliDev/ai-projects/lnca-hooks"
SEMANTIC_SEARCH_DIR="/Volumes/AliDev/ai-projects/semantic-search-service"
TEMPORAL_HOOKS_DIR="/Volumes/AliDev/ai-projects/temporal-hooks"

# Uninstall non-editable versions if they exist
echo "Cleaning up existing installations..."
pip uninstall -y claude-parser lnca-hooks semantic-search-service temporal-hooks-core 2>/dev/null || true

# Install all packages in editable mode
echo "Installing claude-parser in editable mode..."
cd "$CLAUDE_PARSER_DIR"
pip install -e .

echo "Installing lnca-hooks in editable mode..."
cd "$LNCA_HOOKS_DIR"
pip install -e .

# Only install if directories exist
if [ -d "$SEMANTIC_SEARCH_DIR" ]; then
    echo "Installing semantic-search-service in editable mode..."
    cd "$SEMANTIC_SEARCH_DIR"
    pip install -e .
fi

if [ -d "$TEMPORAL_HOOKS_DIR" ]; then
    echo "Installing temporal-hooks in editable mode..."
    cd "$TEMPORAL_HOOKS_DIR"
    pip install -e .
fi

# Verify installations
echo ""
echo "Verifying installations..."
python -c "
import sys
try:
    from claude_parser.hooks.api import execute_hook
    print('✓ claude-parser hooks API available')
except ImportError as e:
    print(f'✗ claude-parser hooks API missing: {e}')
    sys.exit(1)

try:
    from lnca_hooks.resources.executor import lnca_plugin_callback
    print('✓ lnca-hooks executor available')
except ImportError as e:
    print(f'✗ lnca-hooks executor missing: {e}')
    sys.exit(1)

print('')
print('Development environment setup complete!')
"

echo ""
echo "All packages installed in editable mode. Changes to source code will be immediately available."