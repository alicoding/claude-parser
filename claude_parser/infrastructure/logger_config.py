"""Configure loguru to output to stderr only.

This prevents loguru from breaking hooks that need clean stdout for JSON.
"""

import sys
from loguru import logger

# Remove default handler (which outputs to stdout)
logger.remove()

# Add handler that outputs to stderr only
logger.add(sys.stderr, level="INFO")