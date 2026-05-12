"""Convert MS Word (.doc, .docx, .docm) to HTML using mammoth."""

import logging
from pathlib import Path

import mammoth

logger = logging.getLogger(__name__)

WORD_EXTENSIONS = {".doc", ".docx", ".docm"}


def word_to_html(path: Path) -> tuple[str, list[str]]:
    """
    Convert a Word document to HTML.
    Returns (html_string, list of warning messages).
    """
    path = Path(path)
    if path.suffix.lower() not in WORD_EXTENSIONS:
        raise ValueError(f"Not a Word file: {path.suffix}")

    with open(path, "rb") as f:
        result = mammoth.convert_to_html(
            f,
            style_map="""
            p => p
            h1 => h1
            h2 => h2
            h3 => h3
            h4 => h4
            h5 => h5
            h6 => h6
            table => table
            """,
        )

    html = result.value
    messages = result.messages

    # Embed images as base64 if mammoth extracted them (inline images)
    # mammoth returns messages for embedded images; we keep relative paths for now
    # and resolve them in the PDF builder relative to the source file's directory.

    return html, [str(m) for m in messages]
