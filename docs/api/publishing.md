# Publishing Claude Parser

## Overview

Claude Parser can be published to PyPI for public use. The CI/CD pipeline automates most of the process.

## Prerequisites

1. **PyPI Account**: Create accounts at:
   - [PyPI](https://pypi.org) (production)
   - [Test PyPI](https://test.pypi.org) (testing)

2. **API Tokens**: Generate tokens for both PyPI and Test PyPI

3. **GitHub Secrets**: Add to repository settings:
   - `PYPI_API_TOKEN` - Production PyPI token
   - `TEST_PYPI_API_TOKEN` - Test PyPI token

## Release Process

### 1. Prepare Release

```bash
# Run the release preparation script
./scripts/prepare_release.sh

# This will:
# - Check you're on main branch
# - Run all quality checks
# - Build the package
# - Verify the build
```

### 2. Update Version

Edit `pyproject.toml`:
```toml
[tool.poetry]
version = "0.2.0"  # Update this
```

### 3. Update Changelog

Create or update `CHANGELOG.md`:
```markdown
## [0.2.0] - 2025-08-21

### Added
- Full DDD architecture implementation
- Enterprise-grade repository structure
- 95/5 research workflow integration

### Changed
- Improved test coverage to 86%
- Refactored to Domain-Driven Design

### Fixed
- Embedded tool extraction from messages
```

### 4. Commit and Tag

```bash
# Commit changes
git add -A
git commit -m "chore: release v0.2.0"

# Create tag
git tag v0.2.0

# Push to GitHub
git push origin main
git push origin v0.2.0
```

### 5. Create GitHub Release

1. Go to [Releases](https://github.com/anthropics/claude-parser/releases)
2. Click "Create a new release"
3. Select the tag you created
4. Add release notes (can auto-generate)
5. Click "Publish release"

The GitHub Action will automatically:
- Build the package
- Test it
- Publish to Test PyPI first
- Verify installation works
- Publish to production PyPI

## Manual Publishing (if needed)

```bash
# Build the package
poetry build

# Check the package
twine check dist/*

# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ claude-parser

# If all good, upload to PyPI
twine upload dist/*
```

## Verify Publication

After publishing:

```bash
# Install from PyPI
pip install claude-parser

# Test it works
python -c "from claude_parser import load; print('✅ Success!')"
```

## Package Structure

The published package includes:
- `claude_parser/` - Main package with DDD architecture
- `README.md` - Displayed on PyPI page
- `LICENSE` - MIT license
- Dependencies from `pyproject.toml`

## Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality, backward compatible
- **PATCH**: Bug fixes, backward compatible

Examples:
- `0.1.0` → `0.2.0`: Added new features (DDD architecture)
- `0.2.0` → `0.2.1`: Bug fixes only
- `0.2.1` → `1.0.0`: Major API changes

## CI/CD Pipeline

The automated pipeline (`publish.yml`) handles:
1. **Quality Gates** - Tests, linting, coverage
2. **Build** - Creates wheel and source distribution
3. **Test PyPI** - Publishes to test registry first
4. **Verification** - Tests installation from Test PyPI
5. **Production** - Publishes to PyPI if all checks pass

## Troubleshooting

### Build Errors
```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info
poetry build
```

### Upload Errors
```bash
# Check credentials
twine upload --repository testpypi dist/* --verbose
```

### Import Errors After Publishing
- Check all dependencies are in `pyproject.toml`
- Verify `__init__.py` exports are correct
- Test locally first with `pip install -e .`

## Security

- Never commit API tokens
- Use GitHub Secrets for CI/CD
- Rotate tokens regularly
- Use 2FA on PyPI account

## Monitoring

After release:
- Check [PyPI Stats](https://pypistats.org/packages/claude-parser)
- Monitor GitHub issues for problems
- Watch download numbers
- Track version adoption