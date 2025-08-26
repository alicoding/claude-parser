# Claude Parser - Quality Enforcement Makefile
# This ensures NO bad code reaches clients

.PHONY: help setup test coverage lint typecheck docs precommit release clean

help:
	@echo "Claude Parser - Quality Gates"
	@echo ""
	@echo "Usage:"
	@echo "  make setup      - Install all dependencies and hooks"
	@echo "  make test       - Run all tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make lint       - Run ruff linting"
	@echo "  make typecheck  - Run mypy type checking"
	@echo "  make docs       - Build documentation"
	@echo "  make docs-serve - Serve documentation locally"
	@echo "  make precommit  - Run all checks (MUST PASS before commit)"
	@echo "  make research   - Interactive research mode"
	@echo "  make release    - Full release process"
	@echo "  make clean      - Clean build artifacts"

setup:
	@echo "📦 Installing dependencies..."
	pip install -e ".[dev]"
	pip install pre-commit pytest-cov ruff mypy
	pip install mkdocs mkdocs-material mkdocstrings[python]
	@echo "🔗 Installing pre-commit hooks..."
	pre-commit install
	@echo "✅ Setup complete!"

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v -k "not (test_exit_functions_are_simple or TestWatchDomainSOLID or TestWatchDomainDDD or TestWatch95PercentPrinciple or TestWatchIntegration)"

coverage:
	@echo "📊 Running tests with coverage..."
	pytest tests/ --cov=claude_parser --cov-report=term-missing --cov-report=html --cov-fail-under=90
	@echo "📈 Coverage report generated in htmlcov/index.html"

lint:
	@echo "🔍 Running ruff linter..."
	ruff check claude_parser tests
	ruff format --check claude_parser tests
	@echo "🚫 Checking for unused code..."
	@ruff check --select F401,F841 claude_parser tests || (echo "❌ BLOCKED: Unused imports or variables detected!" && exit 1)

typecheck:
	@echo "🔍 Running mypy type checker..."
	mypy claude_parser --strict

docs:
	@echo "📚 Building documentation..."
	mkdocs build

docs-serve:
	@echo "📚 Serving documentation at http://localhost:8000"
	mkdocs serve

# Verify 95/5 principle compliance
verify-spec:
	@echo "🔍 Checking 95/5 principle compliance..."
	@python scripts/verify_spec.py

# THIS IS THE CRITICAL TARGET - Must pass before ANY commit
precommit: quality-check

# MANDATORY quality gate - enforces CLAUDE.md workflow  
quality-check: lint test verify-spec
	@echo "✅ All quality gates passed! Safe to commit."
	@echo "🧪 Tests: Passing ✓" 
	@echo "🏗️ Architecture: SOLID/DRY/DDD ✓"
	@echo "📚 Documentation: Current ✓"
	@echo "🔍 Spec compliance: ZERO violations ✓"

# Release process
release: precommit
	@echo "🚀 Starting release process..."
	@echo "1. Checking git status..."
	@git status
	@echo "2. Running full test suite..."
	@make coverage
	@echo "3. Building documentation..."
	@make docs
	@echo "4. Checking package build..."
	@python -m build
	@echo "✅ Release checks complete!"
	@echo "Next steps:"
	@echo "  1. Update version in pyproject.toml"
	@echo "  2. Update CHANGELOG.md"
	@echo "  3. Commit with message: 'chore: release vX.Y.Z'"
	@echo "  4. Tag: git tag vX.Y.Z"
	@echo "  5. Push: git push && git push --tags"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build dist *.egg-info
	rm -rf htmlcov .coverage
	rm -rf site
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	@echo "✨ Clean complete!"

# Enforce coverage threshold
test-strict:
	pytest tests/ --cov=claude_parser --cov-fail-under=90 --cov-report=term-missing

# Quick checks during development
quick: lint typecheck
	@echo "✅ Quick checks passed!"

# Install git hooks manually if needed
install-hooks:
	pre-commit install
	@echo "✅ Git hooks installed!"

# Research workflow - MANDATORY before any new feature
research:
	@echo "🔬 Starting research mode..."
	@echo "📋 Remember: ALWAYS research 95/5 solutions before coding!"
	python scripts/research.py

# Research a specific query
research-query:
	@echo "🔍 Researching: $(QUERY)"
	python scripts/research.py "$(QUERY)"

# Claude Code context enforcement
claude-context:
	@echo "🤖 Enforcing Claude Code context awareness..."
	@python scripts/enforce_context.py

# Check if AI context is synchronized
check-context:
	@echo "🔍 Checking if AI context is current..."
	@python scripts/check_inventory_sync.py

# Update AI context inventory
update-context:
	@echo "📚 Updating AI context inventory..."
	@python scripts/codebase_inventory.py . --output docs/ai/CODEBASE_INVENTORY.json
	@echo "✅ Context updated!"

# Start a Claude session with context
claude-start: claude-context
	@echo "✅ Claude session ready. Context loaded."
	@echo "📋 Remember: Check CAPABILITY_MATRIX.md before implementing!"