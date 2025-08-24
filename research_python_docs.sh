#!/bin/bash
# Research the best Python documentation tools and practices

# Load environment variables from .env file
export $(cat .env | grep -v '^#' | xargs)

python library_research.py -t "Best Python documentation tools and practices for modern SDKs in 2024-2025" \
  -q "What are the top 3 documentation tools for Python SDKs? Compare Sphinx vs MkDocs vs pdoc vs others. Which has the best looking output and developer experience?" \
  -q "What documentation setup do popular Python libraries use? (like FastAPI, Pydantic, httpx, Rich, Typer, LangChain)" \
  -q "How to generate API documentation from docstrings automatically with type hints and examples? What's the 95/5 solution?" \
  -q "What's the best practice for hosting Python docs? GitHub Pages vs Read the Docs vs Vercel vs custom? Include auto-deployment from CI/CD" \
  -q "What tools create interactive API documentation with live code examples, search, dark mode, and modern UI like Stripe or Vercel docs?"