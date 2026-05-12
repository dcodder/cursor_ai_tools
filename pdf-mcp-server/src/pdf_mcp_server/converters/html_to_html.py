"""Pass-through and XML to HTML handling."""

from pathlib import Path

HTML_EXTENSIONS = {".html", ".htm"}
XML_EXTENSIONS = {".xml", ".xhtml", ".svg"}


def html_to_html(path: Path) -> str:
    """Read HTML file as-is (will be normalized and TOC-injected later)."""
    path = Path(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def xml_to_html(path: Path) -> str:
    """Convert XML to a readable HTML representation (styled pre or tree view)."""
    path = Path(path)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    escaped = (
        content.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f'<div class="xml-document"><pre class="xml-content">{escaped}</pre></div>'
