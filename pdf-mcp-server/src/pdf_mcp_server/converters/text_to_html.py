"""Convert plain text (.txt, .log, etc.) to HTML."""

from pathlib import Path

TEXT_EXTENSIONS = {".txt", ".log", ".text", ".csv", ".ini", ".cfg", ".conf"}


def text_to_html(path: Path) -> str:
    """Convert a text file to HTML with preserved formatting (pre block)."""
    path = Path(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Escape HTML entities
    escaped = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

    return f'<div class="text-document"><pre class="text-content">{escaped}</pre></div>'
