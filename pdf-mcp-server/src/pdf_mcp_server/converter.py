"""Main conversion pipeline: any supported format -> HTML -> PDF with TOC."""

import logging
from pathlib import Path

from .converters import (
    word_to_html,
    text_to_html,
    markdown_to_html,
    html_to_html,
    xml_to_html,
)
from .converters.word_to_html import WORD_EXTENSIONS
from .converters.text_to_html import TEXT_EXTENSIONS
from .converters.markdown_to_html import MD_EXTENSIONS
from .converters.html_to_html import HTML_EXTENSIONS, XML_EXTENSIONS
from .toc import inject_toc
from .styles import PDF_CSS
from .pdf_builder import html_to_pdf

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (
    WORD_EXTENSIONS
    | TEXT_EXTENSIONS
    | MD_EXTENSIONS
    | HTML_EXTENSIONS
    | XML_EXTENSIONS
)


def to_html(path: Path) -> str:
    """Convert supported document to HTML. Raises ValueError if format not supported."""
    path = Path(path).resolve()
    suffix = path.suffix.lower()

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if suffix in WORD_EXTENSIONS:
        html, _ = word_to_html(path)
        return html
    if suffix in TEXT_EXTENSIONS:
        return text_to_html(path)
    if suffix in MD_EXTENSIONS:
        return markdown_to_html(path)
    if suffix in HTML_EXTENSIONS:
        return html_to_html(path)
    if suffix in XML_EXTENSIONS:
        return xml_to_html(path)

    raise ValueError(
        f"Unsupported format: {suffix}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def convert_to_pdf(
    input_path: str | Path,
    output_path: str | Path | None = None,
    add_toc: bool = True,
    toc_depth: int = 3,
) -> str:
    """
    Convert a document to PDF with optional table of contents.

    Args:
        input_path: Path to the source document (.doc, .docx, .docm, .txt, .log, .md, .html, .xml, etc.)
        output_path: Path for the output PDF. If None, same as input with .pdf extension.
        add_toc: Whether to generate a table of contents from headings.
        toc_depth: Maximum heading level in TOC (1–6).

    Returns:
        Absolute path to the created PDF file.
    """
    input_path = Path(input_path).resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".pdf")
    else:
        output_path = Path(output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = to_html(input_path)

    # Wrap fragment in minimal document if needed
    if "<!DOCTYPE" not in html and "<html" not in html.lower():
        html = f"<!DOCTYPE html><html><head><meta charset=\"utf-8\"/></head>{html}</html>"

    if add_toc:
        html = inject_toc(html, toc_depth=toc_depth)

    # Base URL so WeasyPrint can resolve relative image paths (e.g. from Word/mammoth)
    base_url = input_path.parent.as_uri() + "/"

    html_to_pdf(
        html_string=html,
        output_path=output_path,
        base_url=base_url,
        css_string=PDF_CSS,
    )

    return str(output_path)
