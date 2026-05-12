"""Build PDF from HTML. WeasyPrint (best) -> xhtml2pdf (pure Python, Windows) -> pypandoc."""

import tempfile
from pathlib import Path

# Lazy import so the server can start even when WeasyPrint's native deps (e.g. GTK) are missing
_weasyprint_available: bool | None = None
_HTML = _CSS = _FontConfiguration = None


def _ensure_weasyprint() -> bool:
    global _weasyprint_available, _HTML, _CSS, _FontConfiguration
    if _weasyprint_available is not None:
        return _weasyprint_available
    try:
        from weasyprint import HTML as _HTML_cls, CSS as _CSS_cls
        from weasyprint.text.fonts import FontConfiguration as _FC
        _HTML, _CSS, _FontConfiguration = _HTML_cls, _CSS_cls, _FC
        _weasyprint_available = True
    except (ImportError, OSError):
        _weasyprint_available = False
    return _weasyprint_available


def _pdf_via_xhtml2pdf(html_string: str, output_path: Path, base_url: str | None, css_string: str) -> None:
    """Pure Python fallback: works on Windows without GTK or LaTeX."""
    from xhtml2pdf import pisa

    # Inject CSS into HTML so xhtml2pdf can use it
    if "<head>" in html_string:
        html_string = html_string.replace(
            "<head>",
            "<head><style type=\"text/css\">" + css_string + "</style>",
            1,
        )
    else:
        html_string = (
            "<!DOCTYPE html><html><head><meta charset=\"utf-8\"/>"
            "<style type=\"text/css\">" + css_string + "</style></head><body>"
            + html_string + "</body></html>"
        )

    output_path = Path(output_path)
    with open(output_path, "wb") as dest:
        status = pisa.CreatePDF(
            html_string,
            dest=dest,
            path=base_url or "",
            encoding="utf-8",
        )
    if status.err:
        raise RuntimeError("xhtml2pdf reported errors while generating PDF")


def _pdf_via_pypandoc(html_string: str, output_path: Path, base_url: str | None) -> None:
    """Fallback: write HTML to temp file and convert with pandoc (requires pandoc + LaTeX)."""
    try:
        import pypandoc
    except ImportError:
        raise RuntimeError(
            "WeasyPrint and xhtml2pdf are not available. "
            "Install pypandoc and pandoc (with a PDF engine, e.g. LaTeX) for fallback: pip install pypandoc"
        ) from None
    output_path = Path(output_path)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html_string)
        tmp_html = f.name
    try:
        pypandoc.convert_file(
            tmp_html, "pdf", outputfile=str(output_path),
            extra_args=["--standalone", "--toc", "--toc-depth=3"],
        )
    except RuntimeError as e:
        if "pandoc" in str(e).lower() or "not found" in str(e).lower() or "pdflatex" in str(e).lower():
            raise RuntimeError(
                "PDF fallback requires pandoc and a PDF engine (e.g. MiKTeX or TeX Live). "
                "Install pandoc from https://pandoc.org/ and a LaTeX distribution."
            ) from e
        raise
    finally:
        Path(tmp_html).unlink(missing_ok=True)


def html_to_pdf(
    html_string: str,
    output_path: Path,
    base_url: str | None = None,
    css_string: str | None = None,
) -> None:
    """
    Render HTML to PDF.
    Uses WeasyPrint if available; else xhtml2pdf (pure Python, works on Windows); else pypandoc.
    """
    output_path = Path(output_path)
    if _ensure_weasyprint():
        font_config = _FontConfiguration()
        html_doc = _HTML(string=html_string, base_url=base_url)
        styles = []
        if css_string:
            styles.append(_CSS(string=css_string, font_config=font_config))
        html_doc.write_pdf(
            output_path,
            stylesheets=styles,
            font_config=font_config,
        )
        return

    # Use xhtml2pdf (pure Python, works on Windows without GTK/LaTeX)
    from .styles import PDF_CSS_XHTML2PDF
    xhtml2pdf_css = (css_string if (css_string and "target-counter" not in css_string) else None) or PDF_CSS_XHTML2PDF
    try:
        _pdf_via_xhtml2pdf(html_string, output_path, base_url, xhtml2pdf_css)
    except ImportError:
        # xhtml2pdf not installed; try pypandoc
        _pdf_via_pypandoc(html_string, output_path, base_url)
