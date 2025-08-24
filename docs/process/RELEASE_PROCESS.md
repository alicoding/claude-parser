# 🚨 MANDATORY RELEASE PROCESS

## Rule #00: Quality Gates Are NON-NEGOTIABLE

**NO CODE REACHES CLIENTS WITHOUT PASSING ALL GATES**

## Release Process Checklist

### 1. Pre-Development
- [ ] Read SPECIFICATION.md for library choices
- [ ] Check BACKLOG.md for requirements
- [ ] Write tests FIRST (TDD)

### 2. Development
- [ ] Follow 95/5 principle
- [ ] Use approved libraries only
- [ ] Document all public APIs
- [ ] Type hints on everything

### 3. Pre-Commit Gates (LOCAL)
```bash
# These MUST pass before ANY commit
make precommit
```
- [ ] Tests pass (100%)
- [ ] Coverage ≥ 90%
- [ ] Ruff (linting) passes
- [ ] Mypy (type checking) passes
- [ ] Documentation builds

### 4. Commit Message Format
```
type: description

- Detail 1
- Detail 2

Closes #issue
```

Types: feat, fix, docs, test, refactor, style, chore

### 5. Pull Request Gates (CI/CD)
- [ ] All tests pass
- [ ] Coverage maintained/increased
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped (if needed)

### 6. Release Gates
- [ ] All PR checks green
- [ ] Manual testing completed
- [ ] Documentation deployed
- [ ] Tag created
- [ ] PyPI package published

## Enforcement Mechanisms

### Local (Pre-commit hooks)
```bash
# Install hooks (one time)
pre-commit install
```

### CI/CD (GitHub Actions)
- Runs on EVERY push
- Blocks merge if ANY check fails
- No exceptions, no overrides

### Coverage Requirements
- Minimum: 90%
- New code: 100%
- No uncovered critical paths

## Commands

```bash
# Before starting work
make setup

# During development
make test           # Run tests
make coverage       # Check coverage
make lint          # Run linters
make typecheck     # Check types
make docs-serve    # Preview docs

# Before committing
make precommit     # Run ALL checks

# Release
make release       # Full release process
```

## NO EXCEPTIONS

This process protects our users. Shortcuts today become bugs tomorrow.

**If a check fails, FIX IT. Don't bypass it.**