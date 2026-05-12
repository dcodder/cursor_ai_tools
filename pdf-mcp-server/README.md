# PDF MCP Server

An MCP (Model Context Protocol) server that converts documents to PDF with a **table of contents** and clear layout for **tables, images, flowcharts, and text**.

## Supported formats

| Category    | Extensions |
|------------|------------|
| MS Word    | `.doc`, `.docx`, `.docm` |
| Text       | `.txt`, `.log`, `.text`, `.csv`, `.ini`, `.cfg`, `.conf` |
| Markdown   | `.md`, `.markdown`, `.mkd` |
| HTML/XML   | `.html`, `.htm`, `.xml`, `.xhtml`, `.svg` |

## Features

- **Table of contents** – Generated from document headings (H1–H6) with page numbers.
- **Clear tables** – Styled with headers, borders, and alternating row shading.
- **Images** – Preserved and scaled to fit the page; relative paths resolved from the source file location.
- **Code / plain text** – Monospace font and readable blocks for `.txt`, `.log`, and XML.

## Requirements

- **Python 3.10+**
- **WeasyPrint** (and its system dependencies, e.g. Cairo/Pango on Linux/macOS; GTK3 on Windows or use a WeasyPrint-supported stack).

### Windows

The server works on Windows **without WSL**. It uses **xhtml2pdf** (pure Python) when WeasyPrint is not available (WeasyPrint needs GTK/Pango on Windows). No pandoc or LaTeX required. If both WeasyPrint and xhtml2pdf are unavailable, it can fall back to pypandoc (pandoc + LaTeX).

### Linux (Debian/Ubuntu)

```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### macOS

```bash
brew install pango gdk-pixbuf libffi
```

## Install and run

From the project root:

```bash
cd pdf-mcp-server
uv sync
uv run server.py
```

Or with pip:

```bash
pip install -e .
python server.py
```

The server uses **stdio** transport by default (for Cursor, Claude Desktop, etc.).

## MCP tools

- **`convert_document_to_pdf`** – Convert a document to PDF.
  - `input_path` (required): Path to the source file.
  - `output_path` (optional): Path for the output PDF (default: same as input with `.pdf`).
  - `add_toc` (optional): Generate table of contents from headings (default: `true`).
  - `toc_depth` (optional): Max heading level in TOC, 1–6 (default: `3`).

- **`list_supported_formats`** – Returns the list of supported file extensions.

## Cursor configuration

Add to your Cursor MCP config (e.g. in Cursor Settings → MCP, or the project’s MCP config file):

```json
{
  "mcpServers": {
    "pdf-converter": {
      "command": "uv",
      "args": [
        "--directory",
        "D:/AI_Work/pdf-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

Use the absolute path to `pdf-mcp-server` on your machine. If you use `python` instead of `uv`:

```json
{
  "mcpServers": {
    "pdf-converter": {
      "command": "python",
      "args": ["D:/AI_Work/pdf-mcp-server/server.py"]
    }
  }
}
```

## Notes

- **`.doc` (binary Word)** – Converted via the same path as `.docx` (mammoth). For best fidelity with very old `.doc` files, convert to `.docx` first (e.g. with Word or LibreOffice) and then run the server.
- **Images in Word** – Inline images from `.docx`/`.docm` are handled by mammoth; relative image paths in HTML are resolved using the source document’s directory as base URL for WeasyPrint.
- **Charts / flowcharts** – If they are embedded as images in Word or HTML, they are included in the PDF. Native chart objects in Word are not re-rendered; export them as images in the document for best results.
