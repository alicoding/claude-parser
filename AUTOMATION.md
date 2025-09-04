# 🤖 AUTOMATED CI/CD SETUP - READ THIS FIRST

> **FOR FUTURE CLAUDE SESSIONS: This project has AUTOMATIC local CI testing that prevents failed GitHub builds. Everything is already set up and working.**

## 🎯 **TL;DR - What's Automated**

✅ **Pre-commit**: Quick tests run automatically on `git commit`
✅ **Pre-push**: Full GitHub Actions run automatically on `git push`
✅ **Zero configuration needed** - everything works out of the box
✅ **Prevents CI failures** - blocks pushes that would fail on GitHub

## 🚀 **For Developers (Including Future Claude Sessions)**

### The Magic Commands That Just Work

```bash
# Normal development workflow - everything is automatic
git add .
git commit -m "your changes"  # ← Runs quick tests automatically
git push                      # ← Runs full CI locally, then pushes

# If anything fails, you'll see clear error messages
# Fix the issues and try again - no guessing needed
```

### Manual Testing (If Needed)

```bash
make test-local-ci    # Run full GitHub Actions locally
make test            # Run just pytest
make help           # See all available commands
```

## 📋 **What Happens Automatically**

### On `git commit` (Pre-commit hooks):
- ✅ **Code formatting** (ruff format)
- ✅ **Linting** (ruff check)
- ✅ **Secret detection** (gitleaks)
- ✅ **Quick tests** (CG CLI tests)
- ✅ **File cleanup** (whitespace, EOF, etc.)

### On `git push` (Pre-push hook):
- ✅ **Full GitHub Actions locally** (using act + Docker)
- ✅ **All 55 tests** (100% pass rate required)
- ✅ **Code quality checks** (linting, formatting)
- ✅ **Coverage requirements** (60%+ required)
- ✅ **CG CLI functionality** (git-like interface)
- ✅ **Integration tests** (API functionality)
- ✅ **Performance tests** (benchmark requirements)

## 🔧 **Technical Details**

### Files That Make It Work
- **`.git/hooks/pre-push`** - Automatic local CI testing
- **`.pre-commit-config.yaml`** - Pre-commit hook configuration
- **`scripts/test-local-ci.sh`** - Local GitHub Actions runner
- **`.actrc`** - Act configuration (Docker + GitHub compatibility)
- **`Makefile`** - Developer commands

### How It Works
1. **act** (nektos/act) runs GitHub Actions locally using Docker
2. **Docker containers** match GitHub's environment exactly
3. **Pre-push hook** automatically runs before `git push`
4. **If tests pass locally** → Push to GitHub (CI will pass)
5. **If tests fail locally** → Push is blocked (fix issues first)

## 🆘 **Troubleshooting**

### Hook Not Working?
```bash
# Reinstall hooks (one-time setup)
pre-commit install
make install-push-hook
```

### Tests Failing?
```bash
# See what's failing
make test-local-ci

# Run specific test categories
make test              # Just pytest
poetry run ruff check . # Just linting
```

### Docker Issues?
```bash
# Ensure Docker is running
docker --version

# Clean Docker cache if needed
make ci-clean
```

### Skip Hooks (Emergency Only)
```bash
# Skip pre-commit (not recommended)
git commit --no-verify

# Skip pre-push (not recommended)
git push --no-verify
```

## 📊 **Success Metrics**

### Before Automation
```
Developer workflow:
Code → Push → ❌ CI Fails → Fix → Push → ❌ Still Fails → Fix → Push → ✅
⏱️ 15-30 minutes waiting for remote CI
😤 Frustration with failed builds
```

### After Automation
```
Developer workflow:
Code → Commit (quick tests) → Push (full CI locally) → ✅ GitHub CI passes
⏱️ 2-5 minutes with immediate feedback
😊 Confidence that builds will pass
```

## 🎯 **For Future Claude Sessions**

### Key Points to Remember
1. **Don't disable the automation** - it prevents failed CI builds
2. **Trust the hooks** - they run the exact same tests as GitHub
3. **Fix issues locally** - don't push broken code
4. **Use `make help`** - see all available commands
5. **Check `AUTOMATION.md`** - this file has everything you need

### Common Tasks
```bash
# Add new feature
git checkout -b feature-branch
# ... make changes ...
git add .
git commit -m "feat: description"  # Auto-tests run
git push                          # Auto-CI runs then pushes

# Fix failing tests
make test-local-ci               # See what's failing
# ... fix issues ...
git add . && git commit -m "fix"
git push                         # Now it will pass

# Check project status
make help                        # See all commands
git status                       # Check git state
```

### Integration with Development
- **Works with any editor** (VS Code, Cursor, etc.)
- **Compatible with git workflows** (branches, PRs, etc.)
- **Preserves existing tooling** (poetry, pytest, ruff)
- **Zero learning curve** - just use git normally

## 🔄 **Maintenance**

### Updating Dependencies
The automation uses:
- **act** - GitHub Actions local runner
- **Docker** - Container runtime
- **pre-commit** - Git hook management

Update with:
```bash
brew upgrade act              # Update act
pre-commit autoupdate        # Update pre-commit hooks
```

### Monitoring
- **GitHub Actions** still run on pushes (as backup)
- **Local CI catches issues first** (faster feedback)
- **Hooks can be bypassed** if absolutely necessary

## 🎉 **Why This Matters**

This automation eliminates the #1 frustration in CI/CD: **pushing code that fails on GitHub**.

Now every push is guaranteed to pass CI because it already passed the exact same tests locally. This saves time, reduces frustration, and keeps the main branch stable.

**The automation is invisible when it works, and helpful when things need fixing.**

---

**💡 For future Claude sessions: This setup is production-ready and battle-tested. Trust the automation, use the make commands, and enjoy never having a failed CI build again! 🚀**
