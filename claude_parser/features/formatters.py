"""
Feature formatters for documentation.

SOLID: Single Responsibility - Only formatting
95/5: Using toolz for functional operations
"""

from toolz import pipe, map as toolz_map


def to_markdown_table(registry) -> str:
    """Generate markdown table for documentation."""
    header = "| Feature | Category | Status | Tests | Coverage | Notes |\n"
    separator = "|---------|----------|--------|-------|----------|-------|\n"
    
    rows = pipe(
        registry.features,
        lambda features: toolz_map(
            lambda f: f"| {f.name} | {f.category.value} | {f.status.value} | "
                     f"{f'{f.tests_passing}/{f.tests_total}' if f.tests_total else 'N/A'} | "
                     f"{f'{f.coverage_percent:.1f}%' if f.coverage_percent else 'N/A'} | "
                     f"{f.notes or ''} |",
            features
        ),
        lambda rows: "\n".join(rows)
    )
    
    return header + separator + rows