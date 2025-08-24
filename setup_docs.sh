#!/bin/bash
# Setup modern Python documentation with MkDocs + Material theme

echo "📚 Setting up documentation for claude-parser..."

# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-autorefs

# Create MkDocs configuration
cat > mkdocs.yml << 'EOF'
site_name: Claude Parser
site_description: Parse Claude Code JSONL files with ease
site_url: https://yourusername.github.io/claude-parser
repo_url: https://github.com/yourusername/claude-parser
repo_name: claude-parser

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.expand
    - navigation.top
    - search.suggest
    - search.highlight
    - content.tabs.link
    - content.code.annotation
    - content.code.copy
    - content.code.select
  palette:
    - scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  font:
    text: Inter
    code: JetBrains Mono

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          options:
            show_source: true
            show_root_heading: true
            show_signature_annotations: true
            show_symbol_type_heading: true
            show_symbol_type_toc: true
            signature_crossrefs: true
            merge_init_into_class: true
            docstring_style: google

markdown_extensions:
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite
  - pymdownx.snippets
  - pymdownx.superfences
  - admonition
  - pymdownx.details
  - pymdownx.tabbed:
      alternate_style: true
  - def_list
  - pymdownx.tasklist:
      custom_checkbox: true
  - toc:
      permalink: true

nav:
  - Home: index.md
  - Getting Started:
    - Installation: getting-started/installation.md
    - Quick Start: getting-started/quickstart.md
  - User Guide:
    - Basic Usage: guide/basic.md
    - Navigation: guide/navigation.md
    - Discovery: guide/discovery.md
  - API Reference:
    - Core API: api/core.md
    - Models: api/models.md
    - Domain: api/domain.md
  - Examples:
    - Real-world Usage: examples/real-world.md
    - Hook Platform: examples/hooks.md

extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/yourusername
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/claude-parser/
EOF

# Create documentation structure
mkdir -p docs/getting-started docs/guide docs/api docs/examples

# Create main index
cat > docs/index.md << 'EOF'
# Claude Parser

Parse Claude Code JSONL files with ease.

## Features

- 🚀 **Fast** - Uses orjson for blazing fast JSON parsing
- 🎯 **Simple** - 95/5 principle: one line for common tasks
- 🔍 **Navigation** - Search, filter, and navigate conversations
- 🧭 **Discovery** - Auto-find transcripts from working directory
- 📊 **Type-safe** - Full Pydantic models with type hints

## Quick Start

```python
from claude_parser import load, find_current_transcript

# Load current conversation
transcript = find_current_transcript()
conv = load(transcript)

# Search for messages
results = conv.search("95/5 principle")

# Get context around a message
context = conv.get_surrounding(msg.uuid, before=2, after=2)
```

## Installation

```bash
pip install claude-parser
```

## Why Claude Parser?

Built following the 95/5 principle - simple things should be simple, complex things should be possible.
EOF

# Create API reference that auto-generates from code
cat > docs/api/core.md << 'EOF'
# Core API

::: claude_parser
    options:
      show_root_heading: true
      show_source: true
EOF

cat > docs/api/models.md << 'EOF'
# Models

::: claude_parser.models
    options:
      show_root_heading: true
      show_source: true
EOF

cat > docs/api/domain.md << 'EOF'
# Domain

::: claude_parser.domain.conversation
    options:
      show_root_heading: true
      show_source: true
EOF

# Create GitHub Actions workflow for auto-deployment
mkdir -p .github/workflows
cat > .github/workflows/docs.yml << 'EOF'
name: Deploy Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install mkdocs mkdocs-material mkdocstrings[python] mkdocs-autorefs
          pip install -e .
      
      - name: Build docs
        run: mkdocs build
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site/
  
  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
EOF

echo "✅ Documentation setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run 'mkdocs serve' to preview locally at http://localhost:8000"
echo "2. Write your documentation in the docs/ folder"
echo "3. Push to GitHub - docs will auto-deploy to GitHub Pages"
echo ""
echo "🎨 Features included:"
echo "- Auto-generated API docs from docstrings"
echo "- Dark/light mode toggle"
echo "- Search functionality"
echo "- Mobile responsive"
echo "- Code copy buttons"
echo "- Type hints displayed"
echo "- GitHub Pages deployment"