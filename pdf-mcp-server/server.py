"""
PDF MCP Server – Document to PDF conversion with table of contents.

Supports: Word (.doc, .docx, .docm), text (.txt, .log), Markdown (.md),
HTML/XML (.html, .htm, .xml). Output PDFs have a generated TOC and clear
tables, images, and layout.
"""

import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from pdf_mcp_server.converter import convert_to_pdf, SUPPORTED_EXTENSIONS

# Log to stderr so STDIO transport is not corrupted
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("pdf-mcp-server")

mcp = FastMCP("pdf-converter")


@mcp.tool()
def convert_document_to_pdf(
    input_path: str,
    output_path: str | None = None,
    add_toc: bool = True,
    toc_depth: int = 3,
) -> str:
    """Convert a document to PDF with optional table of contents.

    Supported input formats:
    - MS Word: .doc, .docx, .docm
    - Text: .txt, .log, .text, .csv, .ini, .cfg, .conf
    - Markdown: .md, .markdown, .mkd
    - HTML/XML: .html, .htm, .xml, .xhtml, .svg

    Tables, images, and structure are preserved and rendered clearly in the PDF.
    A table of contents is generated from document headings when add_toc is True.

    Args:
        input_path: Absolute or relative path to the source document.
        output_path: Path for the output PDF. If omitted, same as input with .pdf extension.
        add_toc: Whether to generate a table of contents from headings (default True).
        toc_depth: Maximum heading level included in TOC, 1-6 (default 3).

    Returns:
        Absolute path to the created PDF file, or an error message.
    """
    try:
        result = convert_to_pdf(
            input_path=input_path,
            output_path=output_path,
            add_toc=add_toc,
            toc_depth=toc_depth,
        )
        return f"PDF created successfully: {result}"
    except FileNotFoundError as e:
        return f"Error: {e}"
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        logger.exception("Conversion failed")
        return f"Error: {e}"


@mcp.tool()
def list_supported_formats() -> str:
    """List all supported input file extensions for PDF conversion."""
    exts = sorted(SUPPORTED_EXTENSIONS)
    return "Supported extensions: " + ", ".join(exts)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
