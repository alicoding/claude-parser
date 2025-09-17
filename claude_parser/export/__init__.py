"""
Export domain - 100% framework delegation
@FRAMEWORK_FIRST: Only use existing functions
@ZERO_CUSTOM_CODE: No loops, no manual parsing
"""

from .llamaindex import export_for_llamaindex

__all__ = ['export_for_llamaindex']