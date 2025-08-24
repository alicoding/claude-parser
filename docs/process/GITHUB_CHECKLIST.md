# GitHub Push Checklist

## ✅ Completed
- [x] Git initialized with user config
- [x] Branch renamed to `main`
- [x] `.gitignore` updated with security rules
- [x] `.env.example` created with templates
- [x] Security scan script created
- [x] Clean secrets script created
- [x] README for GitHub created

## ⚠️ Remaining Issues

### Security Issues (14 remaining)
Run `python security_scan.py` to see all issues.

Main concerns:
- API keys in research files
- Absolute paths in test files
- Personal email in some files

### Before First Push

1. **Clean remaining secrets**:
   ```bash
   # Check what's staged
   git status
   
   # Don't add sensitive files
   git add --dry-run .
   ```

2. **Create GitHub repo**:
   ```bash
   # Create private repo on GitHub first
   # Then add remote:
   git remote add origin git@github.com:alicoding/claude-parser.git
   ```

3. **Initial commit**:
   ```bash
   # Stage safe files only
   git add README_GITHUB.md
   git add claude_parser/
   git add tests/
   git add pyproject.toml
   git add .gitignore
   
   # Commit
   git commit -m "Initial commit - Claude Parser library"
   
   # Push
   git push -u origin main
   ```

## 🔒 Files to NEVER commit

- `.env` (already in .gitignore)
- Any file with API keys
- Research files with secrets
- Recovered files with personal data
- JSONL files (too large, contain history)

## 📝 Files safe to commit

- Core library code (`claude_parser/`)
- Tests (after cleaning paths)
- Documentation (*.md files)
- Configuration (pyproject.toml, .gitignore)
- Examples (without secrets)

## 🚀 GitHub Settings

After creating repo:
1. Settings → General → Features → Disable Wiki, Projects
2. Settings → Branches → Add rule for `main`:
   - Require pull request reviews
   - Dismiss stale reviews
   - Include administrators
3. Settings → Security → Enable:
   - Dependency graph
   - Dependabot alerts
   - Secret scanning

## 📦 Future: Publishing to PyPI

When ready to publish:
1. Clean all secrets thoroughly
2. Add proper versioning
3. Create release workflow
4. Register on PyPI
5. Use GitHub Actions for CI/CD