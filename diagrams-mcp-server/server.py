"""
Diagrams MCP Server – Create diagrams (Mermaid), tables, figures, and data charts.

Outputs: Markdown (Mermaid, tables) and image files (PNG, SVG).
"""

import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from diagrams_mcp_server.chart import create_chart as _create_chart
from diagrams_mcp_server.mermaid import render_mermaid_to_image as _render_mermaid
from diagrams_mcp_server.table import create_table as _create_table

# Log to stderr so STDIO transport is not corrupted
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s %(levelname)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("diagrams-mcp-server")

mcp = FastMCP("diagrams")


@mcp.tool()
def create_table(
    headers: list[str],
    rows: list[list],
    format: str = "markdown",
    caption: str | None = None,
) -> str:
    """Generate a markdown or HTML table from structured data.

    Args:
        headers: Column headers.
        rows: Row data (each row is a list of cell values).
        format: "markdown" or "html".
        caption: Optional table caption.

    Returns:
        Table as markdown or HTML string.
    """
    try:
        return _create_table(
            headers=headers,
            rows=rows,
            format=format,
            caption=caption,
        )
    except Exception as e:
        logger.exception("create_table failed")
        return f"Error: {e}"


@mcp.tool()
def create_chart(
    chart_type: str,
    data: dict,
    output_path: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
) -> str:
    """Generate a data chart and save as PNG or SVG.

    Args:
        chart_type: "bar", "line", "pie", or "scatter".
        data: For bar/line/pie: {"labels": [...], "values": [...]}.
              For scatter: {"x": [...], "y": [...]}.
        output_path: Path for output file (extension .png or .svg).
        title: Optional chart title.
        x_label: Optional x-axis label.
        y_label: Optional y-axis label.

    Returns:
        Absolute path to saved image. For bar/line charts, also includes
        optional Mermaid xychart-beta markdown.
    """
    try:
        path, mermaid_md = _create_chart(
            chart_type=chart_type,
            data=data,
            output_path=output_path,
            title=title,
            x_label=x_label,
            y_label=y_label,
        )
        result = f"Chart saved to: {path}"
        if mermaid_md:
            result += f"\n\nMermaid xychart (for markdown):\n{mermaid_md}"
        return result
    except ValueError as e:
        return f"Error: {e}"
    except Exception as e:
        logger.exception("create_chart failed")
        return f"Error: {e}"


@mcp.tool()
def create_mermaid_diagram(
    mermaid_code: str,
    output_path: str | None = None,
    format: str = "markdown_only",
    theme: str = "default",
) -> str:
    """Generate a Mermaid diagram and optionally render to image.

    Args:
        mermaid_code: Raw Mermaid diagram code (flowchart, sequenceDiagram, etc.).
        output_path: Path for image file when format is png, svg, or both.
        format: "markdown_only", "png", "svg", or "both".
        theme: "default", "dark", or "neutral".

    Returns:
        Markdown fenced block with Mermaid code. If format is png/svg/both,
        also renders to image and returns absolute path(s).
    """
    markdown = "```mermaid\n" + mermaid_code.strip() + "\n```"
    if format == "markdown_only":
        return markdown

    if not output_path:
        return f"Error: output_path is required when format is {format}.\n\n{markdown}"

    try:
        out = Path(output_path).resolve()
        paths: list[str] = []

        if format in ("png", "both"):
            png_path = str(out.with_suffix(".png"))
            _render_mermaid(mermaid_code, png_path, theme)
            paths.append(png_path)

        if format in ("svg", "both"):
            svg_path = str(out.with_suffix(".svg"))
            _render_mermaid(mermaid_code, svg_path, theme)
            paths.append(svg_path)

        result = markdown
        if paths:
            result += f"\n\nImage(s) saved to: {', '.join(paths)}"
        return result
    except Exception as e:
        logger.exception("create_mermaid_diagram failed")
        return f"Error: {e}\n\n{markdown}"


@mcp.tool()
def render_mermaid_to_image(
    mermaid_code: str,
    output_path: str,
    theme: str = "default",
) -> str:
    """Render existing Mermaid code to PNG or SVG.

    Requires Node.js and @mermaid-js/mermaid-cli (installed via npx if not present).

    Args:
        mermaid_code: Mermaid diagram code.
        output_path: Path for output (extension .png or .svg determines format).
        theme: "default", "dark", or "neutral".

    Returns:
        Absolute path to created image.
    """
    try:
        path = _render_mermaid(mermaid_code, output_path, theme)
        return f"Image saved to: {path}"
    except Exception as e:
        logger.exception("render_mermaid_to_image failed")
        return f"Error: {e}"


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
