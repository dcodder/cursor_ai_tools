"""Convert Markdown to HTML with extensions for tables and code."""

from pathlib import Path

import markdown

MD_EXTENSIONS = {".md", ".markdown", ".mkd"}


def markdown_to_html(path: Path) -> str:
    """Convert Markdown file to HTML with tables, fenced code, etc."""
    path = Path(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    html = markdown.markdown(
        content,
        extensions=[
            "extra",  # tables, fenced code, footnotes, etc.
            "nl2br",
        ],
    )
    return html
