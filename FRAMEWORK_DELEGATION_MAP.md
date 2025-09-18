# Framework Delegation Map for UI-Ready API
@FRAMEWORK_FIRST @ZERO_CUSTOM_CODE @NEURAL_TIMESTAMP: 2025-09-17T23:45:00Z

## Core Philosophy
Every formatting task MUST delegate to a framework with ZERO custom code.
If a library requires boilerplate → REJECT and find better.

## Number & Data Formatting

### ✅ Numbers with Commas
**Framework:** `humanize`
```python
humanize.intcomma(45678)  # → "45,678"
```
**Neural Path:** @NUMBER_FORMAT → humanize.intcomma

### ✅ Currency
**Framework:** `babel`
```python
format_currency(12.45, 'USD', locale='en_US')  # → "$12.45"
```
**Neural Path:** @CURRENCY_FORMAT → babel.format_currency

### ✅ Time Duration
**Framework:** `humanfriendly`
```python
humanfriendly.format_timespan(10800, detailed=False)  # → "3 hours"
```
**Neural Path:** @DURATION_FORMAT → humanfriendly.format_timespan

### ✅ File Sizes
**Framework:** `humanize`
```python
humanize.naturalsize(1048576)  # → "1.0 MB"
```
**Neural Path:** @FILESIZE_FORMAT → humanize.naturalsize

### ✅ Timestamps to Human Time
**Framework:** `arrow`
```python
arrow.get(timestamp).humanize()  # → "2 hours ago"
arrow.get(timestamp).format('h:mm A')  # → "2:34 PM"
```
**Neural Path:** @TIME_FORMAT → arrow.humanize/format

### ✅ Pluralization
**Framework:** `inflect`
```python
p = inflect.engine()
p.plural_noun("message", 5)  # → "messages"
f"{count} {p.plural_noun('message', count)}"  # → "5 messages"
```
**Neural Path:** @PLURALIZE → inflect.plural_noun

## Display Formatting

### ✅ Markdown to HTML
**Framework:** `markdown2` (better than markdown - more features, less setup)
```python
markdown2.markdown(text, extras=['fenced-code-blocks'])  # → HTML with syntax highlighting
```
**Neural Path:** @MARKDOWN_HTML → markdown2.markdown

### ✅ Syntax Highlighting
**Framework:** `pygments`
```python
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
highlight(code, PythonLexer(), HtmlFormatter())  # → Colored HTML
```
**Neural Path:** @SYNTAX_HIGHLIGHT → pygments.highlight

### ✅ Pretty JSON
**Framework:** `rich`
```python
from rich.json import JSON
from rich.console import Console
Console().print(JSON(json_str))  # → Colored, formatted JSON
```
**Neural Path:** @JSON_PRETTY → rich.JSON

### ✅ Tables
**Framework:** `tabulate`
```python
from tabulate import tabulate
tabulate(data, headers="keys", tablefmt="github")  # → GitHub markdown table
```
**Neural Path:** @TABLE_FORMAT → tabulate

### ✅ Diffs
**Framework:** `deepdiff` (for data) + `difflib` (for text)
```python
from deepdiff import DeepDiff
DeepDiff(old, new, view='text')  # → Human-readable diff

import difflib
'\n'.join(difflib.unified_diff(old.splitlines(), new.splitlines()))  # → Unix diff
```
**Neural Path:** @DIFF_FORMAT → deepdiff/difflib

## Status & Progress

### ✅ Progress Bars
**Framework:** `rich.progress`
```python
from rich.progress import track
for item in track(items, description="Processing..."):
    pass  # → Live progress bar
```
**Neural Path:** @PROGRESS_BAR → rich.progress.track

### ✅ Status with Emojis
**Framework:** `rich` + `emoji`
```python
from emoji import emojize
emojize(":white_check_mark: Success")  # → "✅ Success"
emojize(":x: Failed")  # → "❌ Failed"
```
**Neural Path:** @STATUS_EMOJI → emoji.emojize

### ✅ Colored Terminal Output
**Framework:** `rich.console`
```python
from rich.console import Console
console = Console()
console.print("[green]✓[/green] Success")  # → Colored output
```
**Neural Path:** @COLOR_OUTPUT → rich.console

## Export Formats

### ✅ HTML Reports
**Framework:** `jinja2`
```python
from jinja2 import Template
Template(html_template).render(data=session_data)  # → Complete HTML
```
**Neural Path:** @HTML_REPORT → jinja2.Template

### ✅ PDF Export
**Framework:** `weasyprint`
```python
from weasyprint import HTML
HTML(string=html_content).write_pdf('output.pdf')  # → PDF file
```
**Neural Path:** @PDF_EXPORT → weasyprint.HTML

### ✅ Excel Export
**Framework:** `xlsxwriter`
```python
import xlsxwriter
workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write_row(0, 0, headers)
```
**Neural Path:** @EXCEL_EXPORT → xlsxwriter

## Data Validation & Defaults

### ✅ Handle None/Empty
**Framework:** `more-itertools`
```python
from more_itertools import first
first(messages, default="No messages found")  # → Safe default
```
**Neural Path:** @SAFE_DEFAULT → more_itertools.first

### ✅ Type Conversion
**Framework:** `pydantic`
```python
from pydantic import BaseModel
class Output(BaseModel):
    message: str = "No data"
Output(**data).message  # → Always returns string
```
**Neural Path:** @TYPE_SAFETY → pydantic.BaseModel

## Composite Functions Map

```python
def get_session_summary(session) -> str:
    """One-liner using pure framework delegation"""
    # Uses: humanize.intcomma + babel.format_currency + humanfriendly.format_timespan
    return f"{humanize.intcomma(msg_count)} messages, {humanfriendly.format_timespan(duration)}, {format_currency(cost, 'USD')}"

def get_formatted_message(msg) -> str:
    """One-liner markdown formatting"""
    # Uses: emoji.emojize + arrow.format
    return f"{emojize(':speech_balloon:')} **{msg['role']}** ({arrow.get(msg['timestamp']).format('h:mm A')}): {msg['content']}"

def export_as_html(session) -> str:
    """One-liner HTML generation"""
    # Uses: jinja2.Template + markdown2.markdown
    return Template(HTML_TEMPLATE).render(
        messages=[markdown2.markdown(m) for m in messages]
    )
```

## Framework Requirements

Add to pyproject.toml:
```toml
[tool.poetry.dependencies]
humanize = "^4.0"
babel = "^2.0"
humanfriendly = "^10.0"
arrow = "^1.0"
inflect = "^7.0"
markdown2 = "^2.4"
pygments = "^2.0"
rich = "^13.0"
tabulate = "^0.9"
deepdiff = "^6.0"
emoji = "^2.0"
jinja2 = "^3.0"
weasyprint = "^60.0"
xlsxwriter = "^3.0"
more-itertools = "^10.0"
pydantic = "^2.0"
```

## Neural Navigation Index

- @NUMBER_FORMAT → humanize
- @CURRENCY_FORMAT → babel
- @DURATION_FORMAT → humanfriendly
- @FILESIZE_FORMAT → humanize
- @TIME_FORMAT → arrow
- @PLURALIZE → inflect
- @MARKDOWN_HTML → markdown2
- @SYNTAX_HIGHLIGHT → pygments
- @JSON_PRETTY → rich
- @TABLE_FORMAT → tabulate
- @DIFF_FORMAT → deepdiff/difflib
- @PROGRESS_BAR → rich.progress
- @STATUS_EMOJI → emoji
- @COLOR_OUTPUT → rich.console
- @HTML_REPORT → jinja2
- @PDF_EXPORT → weasyprint
- @EXCEL_EXPORT → xlsxwriter
- @SAFE_DEFAULT → more_itertools
- @TYPE_SAFETY → pydantic

## Implementation Rule

EVERY feature function MUST:
1. Use ONLY framework calls
2. Return display-ready strings
3. Handle empty/None via framework defaults
4. Be a one-liner or max 3 lines
5. ZERO custom formatting logic

Example violation:
```python
# ❌ WRONG - Custom formatting
def format_cost(amount):
    return f"${amount:.2f}"  # Custom logic!

# ✅ RIGHT - Framework delegation
def format_cost(amount):
    return format_currency(amount, 'USD')  # Framework handles it!
```