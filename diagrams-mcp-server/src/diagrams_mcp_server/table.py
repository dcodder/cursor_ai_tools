"""Table generation – Markdown and HTML tables from structured data."""

import html
from typing import Any


def create_table(
    headers: list[str],
    rows: list[list[Any]],
    format: str = "markdown",
    caption: str | None = None,
) -> str:
    """Generate a markdown or HTML table from headers and rows.

    Args:
        headers: Column headers.
        rows: Row data (each row is a list of cell values).
        format: "markdown" or "html".
        caption: Optional table caption.

    Returns:
        Table as markdown or HTML string.
    """
    if format == "html":
        return _create_html_table(headers, rows, caption)
    return _create_markdown_table(headers, rows, caption)


def _create_markdown_table(
    headers: list[str],
    rows: list[list[Any]],
    caption: str | None,
) -> str:
    """Generate a markdown table."""
    lines: list[str] = []

    def cell_str(val: Any) -> str:
        s = str(val) if val is not None else ""
        # Escape pipe characters in markdown
        return s.replace("|", "\\|")

    # Header row
    header_cells = [cell_str(h) for h in headers]
    lines.append("| " + " | ".join(header_cells) + " |")

    # Separator row
    lines.append("| " + " | ".join("---" for _ in headers) + " |")

    # Data rows
    for row in rows:
        # Pad row if shorter than headers
        padded = list(row)[: len(headers)]
        while len(padded) < len(headers):
            padded.append("")
        cells = [cell_str(c) for c in padded]
        lines.append("| " + " | ".join(cells) + " |")

    result = "\n".join(lines)
    if caption:
        result = f"{result}\n\n*{caption}*"
    return result


def _create_html_table(
    headers: list[str],
    rows: list[list[Any]],
    caption: str | None,
) -> str:
    """Generate an HTML table."""
    parts: list[str] = ["<table>"]
    if caption:
        parts.append(f"  <caption>{html.escape(caption)}</caption>")

    # Header
    parts.append("  <thead>")
    parts.append("    <tr>")
    for h in headers:
        parts.append(f"      <th>{html.escape(str(h))}</th>")
    parts.append("    </tr>")
    parts.append("  </thead>")

    # Body
    parts.append("  <tbody>")
    for row in rows:
        padded = list(row)[: len(headers)]
        while len(padded) < len(headers):
            padded.append("")
        parts.append("    <tr>")
        for c in padded:
            parts.append(f"      <td>{html.escape(str(c) if c is not None else "")}</td>")
        parts.append("    </tr>")
    parts.append("  </tbody>")
    parts.append("</table>")

    return "\n".join(parts)
