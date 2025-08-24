#!/bin/bash
# Setup Quality Gates - This MUST be run before any development

set -e  # Exit on any error

echo "🚨 Setting up MANDATORY Quality Gates for Claude Parser"
echo "=================================================="
echo ""

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "📍 Python version: $python_version"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -e ".[dev]" || pip install -e . && pip install pytest pytest-cov mypy ruff pre-commit bandit mkdocs mkdocs-material "mkdocstrings[python]"

# Setup pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]

  - repo: local
    hooks:
      - id: test-coverage
        name: Test Coverage Check
        entry: bash -c 'pytest tests/ --cov=claude_parser --cov-fail-under=90'
        language: system
        pass_filenames: false
        always_run: true
EOF

pre-commit install

# Create git hooks directly (backup in case pre-commit fails)
echo "🔒 Creating git hooks..."
mkdir -p .git/hooks

cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "🔍 Running quality gates..."

# Run tests with coverage
echo "📊 Checking test coverage..."
pytest tests/ --cov=claude_parser --cov-fail-under=90 --quiet
if [ $? -ne 0 ]; then
    echo "❌ Test coverage below 90%. Commit blocked."
    exit 1
fi

# Run linting
echo "🔍 Running linter..."
ruff check claude_parser tests
if [ $? -ne 0 ]; then
    echo "❌ Linting failed. Fix issues before committing."
    exit 1
fi

# Run type checking
echo "🔍 Running type checker..."
mypy claude_parser --ignore-missing-imports
if [ $? -ne 0 ]; then
    echo "❌ Type checking failed. Fix issues before committing."
    exit 1
fi

echo "✅ All quality gates passed!"
EOF

chmod +x .git/hooks/pre-commit

# Verify setup
echo ""
echo "🔍 Verifying setup..."
echo ""

# Check if Makefile exists
if [ -f Makefile ]; then
    echo "✅ Makefile found"
else
    echo "❌ Makefile missing - creating..."
    curl -s https://raw.githubusercontent.com/your-repo/claude-parser/main/Makefile > Makefile
fi

# Run initial checks
echo ""
echo "🧪 Running initial quality checks..."
echo ""

# Create tests directory if it doesn't exist
mkdir -p tests
if [ ! -f tests/__init__.py ]; then
    touch tests/__init__.py
fi

# Try to run tests
pytest tests/ --quiet 2>/dev/null || echo "⚠️  No tests found yet - remember TDD!"

echo ""
echo "✅ Quality Gates Setup Complete!"
echo ""
echo "📋 MANDATORY WORKFLOW:"
echo "  1. Write tests FIRST (TDD)"
echo "  2. Run 'make test' frequently"
echo "  3. Run 'make precommit' before EVERY commit"
echo "  4. Commits will be BLOCKED if quality gates fail"
echo ""
echo "🚨 REMEMBER: Rule #00 - NO CODE REACHES CLIENTS WITHOUT PASSING ALL GATES"
echo ""
echo "Run 'make help' to see all available commands"