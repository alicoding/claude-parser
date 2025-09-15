# Dependency Management Bug Analysis & Solution Plan

## Executive Summary
We have a critical dependency management issue between `claude-parser` and `lnca-hooks` packages that demonstrates a fundamental problem in Python package development: managing interdependent packages during active development.

## The Problem

### Current Situation
1. **claude-parser** has new API modules (`hooks.api`) in local development
2. **lnca-hooks** depends on these new modules
3. When lnca-hooks runs as a CLI tool (`lnca-hooks stop`), it fails with:
   ```
   ModuleNotFoundError: No module named 'claude_parser.hooks.api'
   ```

### Root Cause Analysis
The issue stems from multiple installation states:
- `claude-parser` is installed in editable mode (`pip install -e .`)
- The editable install points to `/Volumes/AliDev/ai-projects/claude-parser/`
- The `hooks.api` module EXISTS in the source code
- But when `lnca-hooks` runs as a CLI entry point, it's not finding the module

### Why This Happens
1. **Entry Point Execution Context**: When `lnca-hooks` runs from `/opt/homebrew/Caskroom/miniconda/base/bin/lnca-hooks`, it may not have the correct Python path
2. **Package Metadata Mismatch**: The installed package metadata may not reflect the current source structure
3. **Import Resolution Order**: Python's import system may be caching old module structures

## The Broader Pattern Problem

### God Object Anti-Pattern Impact
Our refactoring removed `RichMessage`/`RichSession` god objects, which had these consequences:
1. **Hidden Dependencies**: We couldn't see all the places that depended on these types
2. **Cascading Failures**: Changes in one package broke dependent packages
3. **No Semantic Understanding**: We lacked tools to understand the full dependency graph

### Missing Infrastructure
1. **No Semantic Search Integration**: Can't query "what depends on claude_parser.hooks.api?"
2. **No Dependency Graph Visualization**: Can't see the full impact of changes
3. **No Automated Compatibility Testing**: Changes aren't tested against dependent packages

## Proposed Solution

### Immediate Fix (Tactical)
```bash
# 1. Reinstall both packages in development mode
pip uninstall claude-parser lnca-hooks -y
cd /Volumes/AliDev/ai-projects/claude-parser
pip install -e .
cd /Volumes/AliDev/ai-projects/lnca-hooks
pip install -e .

# 2. Verify the installation
python -c "from claude_parser.hooks.api import execute_hook; print('Success!')"
```

### Long-term Solution (Strategic)

#### 1. Development Environment Setup
Create a development setup script that ensures consistent environment:
```bash
#!/bin/bash
# dev-setup.sh
pip install -e /Volumes/AliDev/ai-projects/claude-parser
pip install -e /Volumes/AliDev/ai-projects/lnca-hooks
pip install -e /Volumes/AliDev/ai-projects/semantic-search-service
```

#### 2. Dependency Declaration
In `lnca-hooks/pyproject.toml`:
```toml
[tool.poetry.dependencies]
# For development, use local path
claude-parser = {path = "../claude-parser", develop = true}

# For production, use version constraint
# claude-parser = "^2.0.0"
```

#### 3. Pre-commit Hooks
Add dependency validation before commits:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-imports
        name: Verify claude-parser imports
        entry: python -c "from claude_parser.hooks.api import execute_hook"
        language: system
        pass_filenames: false
```

#### 4. Semantic Search Integration
Implement a workflow that:
1. Before any refactoring, searches for all usages across projects
2. Maps the full dependency graph
3. Creates a migration plan that updates all dependencies

#### 5. API Versioning Strategy
```python
# claude_parser/hooks/__init__.py
__version__ = "1.0.0"
__all__ = ["execute_hook", "parse_hook_input", ...]

# Maintain backward compatibility
try:
    from .api import *
except ImportError:
    # Fallback for older versions
    from .legacy_api import *
```

## Pattern Recognition

### The God Object Pattern
**Symptoms:**
- Classes with 10+ fields/methods
- Many imports from a single module
- Tight coupling across package boundaries

**Solution:**
- Pure functions operating on plain data (dicts)
- @COMPOSITION pattern
- Domain-specific utilities instead of shared types

### The Dependency Chain Pattern
**Symptoms:**
- Package A needs development version of Package B
- Changes in one package break others
- Import errors only discovered at runtime

**Solution:**
- Editable installs for all related packages
- Automated dependency testing
- Semantic search for impact analysis

## Action Items

### Immediate (Today)
1. ✅ Document the issue comprehensively (this document)
2. 🔄 Fix the immediate import issue with proper editable installs
3. 🔄 Test the fix across all hook events

### Short-term (This Week)
1. 📋 Create dev-setup.sh script for consistent environment
2. 📋 Add import validation tests
3. 📋 Document the development workflow

### Long-term (This Month)
1. 📋 Integrate semantic search for dependency analysis
2. 📋 Create automated compatibility testing
3. 📋 Implement proper API versioning

## Lessons Learned

1. **God objects create viral dependencies** - One shared type infects the entire codebase
2. **Python's import system is complex** - Editable installs, entry points, and module resolution interact in unexpected ways
3. **Semantic understanding is critical** - We need tools to understand code relationships before making changes
4. **@COMPOSITION over inheritance** - Plain data structures (dicts) are more maintainable than complex class hierarchies

## Recommended Reading
- [Python Packaging Best Practices](https://packaging.python.org/tutorials/packaging-projects/)
- [Circular Dependencies in Python](https://www.mend.io/blog/closing-the-loop-on-python-circular-import-issue/)
- [Editable Installs Guide](https://pip.pypa.io/en/stable/topics/local-project-installs/)

## Conclusion
This bug exemplifies why we need:
1. **Semantic search** to understand dependencies
2. **@COMPOSITION pattern** to avoid god objects
3. **Proper development environment setup** for interdependent packages
4. **Automated testing** across package boundaries

The immediate fix is simple (reinstall in editable mode), but the long-term solution requires architectural changes to prevent these issues.