# Local CI/CD Testing Guide

> **Test GitHub Actions locally before pushing to avoid failed builds**

This guide explains how to run your GitHub Actions workflows locally using `act`, eliminating the frustrating cycle of push → CI fails → fix → push again.

## 🚀 Quick Start

### Prerequisites

1. **Install act** (GitHub Actions local runner):
   ```bash
   # macOS
   brew install act

   # npm
   npm install -g @nektos/act
   ```

2. **Ensure Docker is running**:
   ```bash
   docker --version  # Should show Docker version
   ```

### Basic Usage

```bash
# Run all GitHub Actions locally
make test-local-ci

# Or use the script directly
./scripts/test-local-ci.sh

# Show available commands
make help
```

## 📋 Available Commands

### Make Commands (Recommended)

```bash
make test-local-ci    # Run GitHub Actions locally
make ci-info          # Show workflow information
make ci-clean         # Clean act cache
make push-safe        # Test locally then push (recommended workflow)
make install-push-hook # Install automatic pre-push testing
```

### Direct Script Commands

```bash
./scripts/test-local-ci.sh all     # Run all workflows (default)
./scripts/test-local-ci.sh ci      # Run CI workflow only
./scripts/test-local-ci.sh pr      # Run as pull request
./scripts/test-local-ci.sh info    # Show workflow information
./scripts/test-local-ci.sh clean   # Clean cache
./scripts/test-local-ci.sh help    # Show help
```

## 🔄 Recommended Workflow

### Option 1: Manual Testing (Safe)
```bash
# 1. Make your changes
git add .
git commit -m "feat: your changes"

# 2. Test locally before pushing
make test-local-ci

# 3. Push only if local tests pass
git push
```

### Option 2: Automated Pre-Push Hook (Automatic)
```bash
# 1. Install pre-push hook (one time setup)
make install-push-hook

# 2. Now every push automatically tests locally first
git push  # Will automatically run local CI before pushing
```

### Option 3: Super Safe Workflow
```bash
# Use the combined command that tests then pushes
make push-safe
```

## ⚙️ Configuration

### Act Configuration (`.actrc`)
```bash
# Use larger runner image for better GitHub compatibility
-P ubuntu-latest=catthehacker/ubuntu:act-latest
--verbose
--reuse
--pull=false
--use-host-network
```

### Secrets Configuration (`.secrets`)
```bash
# Add secrets needed for your workflows
PYTHON_VERSION=3.11
# PYPI_TOKEN=your_token_here (if needed)
```

## 🔧 How It Works

### What `act` Does
1. **Parses** your `.github/workflows/*.yml` files
2. **Spins up** Docker containers matching GitHub's environment
3. **Executes** the exact same steps as GitHub Actions
4. **Reports** results locally before you push

### What Gets Tested
- ✅ **Python tests** (pytest with all your test files)
- ✅ **Code quality** (ruff linting and formatting)
- ✅ **Coverage** (test coverage requirements)
- ✅ **CG CLI** (your git-like interface functionality)
- ✅ **Integration tests** (API functionality)
- ✅ **Performance tests** (benchmark requirements)

## 📊 Example Output

### Successful Run
```bash
🚀 Starting Local GitHub Actions Testing
==================================================
📋 Checking prerequisites...
✅ Prerequisites satisfied
📊 Current git status: (clean)

🔄 Running workflow: ci.yml
--------------------------------------------------
🐳 Pulling Docker image: catthehacker/ubuntu:act-latest
📦 Installing dependencies...
🧪 Running Python tests...
✅ 55 tests passed
🔍 Checking code quality...
✅ No linting issues
📈 Checking test coverage...
✅ Coverage: 87% (above 60% threshold)
🎮 Testing CG CLI...
✅ CG CLI tests passed

✅ Workflow ci.yml passed locally!
🎉 Local testing completed successfully!
✅ Your changes should pass GitHub Actions
💡 Now you can safely push to GitHub: git push
```

### Failed Run
```bash
❌ Workflow ci.yml failed locally!
🔧 Fix the issues before pushing to GitHub

# Details about what failed will be shown above
```

## 🐛 Troubleshooting

### Common Issues

**Docker not running:**
```bash
# Start Docker Desktop or daemon
open -a Docker  # macOS
```

**act not installed:**
```bash
brew install act  # macOS
npm install -g @nektos/act  # Cross-platform
```

**Permission errors:**
```bash
chmod +x scripts/test-local-ci.sh
chmod +x .pre-push
```

**Slow first run:**
```bash
# First run downloads Docker images (takes time)
# Subsequent runs are much faster due to caching
```

### Debug Mode

```bash
# Run with verbose output for debugging
act --verbose

# Or use the script with more details
./scripts/test-local-ci.sh ci
```

### Clean Slate

```bash
# Clean all caches and start fresh
make ci-clean
docker system prune -f
```

## 📈 Performance Tips

1. **Reuse containers**: act caches containers between runs
2. **Don't pull images**: configured to skip unnecessary pulls
3. **Use host network**: faster networking for dependencies
4. **Parallel execution**: multiple jobs run in parallel like GitHub

## 🎯 Benefits

### Before (Traditional Workflow)
```
Code → Push → ❌ CI Fails → Fix → Push → ❌ Still Fails → Fix → Push → ✅ Finally Works
⏱️ 15-30 minutes of waiting and frustration
```

### After (With Local CI)
```
Code → Test Locally → Fix Issues → Push → ✅ CI Passes
⏱️ 2-5 minutes, instant feedback, no waiting
```

### Savings
- **Time**: No waiting for remote CI runs
- **Bandwidth**: No unnecessary pushes
- **Frustration**: Immediate feedback on issues
- **Team**: No broken builds affecting others
- **GitHub Actions minutes**: Reduced usage (if on paid plan)

## 🔗 Integration with Development Workflow

### VS Code Integration
1. Install "GitHub Local Actions" extension
2. Run act directly from VS Code
3. Integrated terminal output

### Git Aliases
```bash
# Add to ~/.gitconfig
[alias]
    test-push = !make test-local-ci && git push
    safe-push = !make push-safe
```

### Shell Aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias gtp="make test-local-ci && git push"  # git test push
alias gsp="make push-safe"                  # git safe push
```

## 📚 Additional Resources

- [act Documentation](https://github.com/nektos/act)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)

## 🆘 Need Help?

1. **Check logs**: act provides detailed output about what's failing
2. **Run manually**: Use individual make commands to isolate issues
3. **Clean cache**: `make ci-clean` for a fresh start
4. **Check Docker**: Ensure Docker has enough resources allocated

---

**💡 Pro Tip**: Set up the pre-push hook for automatic testing, then you never have to remember to test locally—it happens automatically!
