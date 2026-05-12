"""Chart generation – Data charts via matplotlib, saved as PNG or SVG."""

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Headless backend
import matplotlib.pyplot as plt


def create_chart(
    chart_type: str,
    data: dict[str, list[Any]],
    output_path: str,
    title: str | None = None,
    x_label: str | None = None,
    y_label: str | None = None,
) -> tuple[str, str | None]:
    """Generate a data chart and save as PNG or SVG.

    Args:
        chart_type: "bar", "line", "pie", or "scatter".
        data: For bar/line/pie: {"labels": [...], "values": [...]}.
              For scatter: {"x": [...], "y": [...]}.
        output_path: Path for output file (extension determines PNG vs SVG).
        title: Optional chart title.
        x_label: Optional x-axis label.
        y_label: Optional y-axis label.

    Returns:
        Tuple of (absolute path to saved image, optional Mermaid xychart-beta markdown).
    """
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    mermaid_md: str | None = None

    if chart_type == "bar":
        labels = data.get("labels", [])
        values = data.get("values", [])
        if not labels or not values:
            raise ValueError("Bar chart requires 'labels' and 'values' in data")
        _create_bar_chart(labels, values, out, title, x_label, y_label)
        mermaid_md = _bar_to_mermaid_xychart(labels, values, title)

    elif chart_type == "line":
        labels = data.get("labels", data.get("x", []))
        values = data.get("values", data.get("y", []))
        if not labels or not values:
            raise ValueError("Line chart requires 'labels'/'values' or 'x'/'y' in data")
        _create_line_chart(labels, values, out, title, x_label, y_label)
        mermaid_md = _line_to_mermaid_xychart(labels, values, title)

    elif chart_type == "pie":
        labels = data.get("labels", [])
        values = data.get("values", [])
        if not labels or not values:
            raise ValueError("Pie chart requires 'labels' and 'values' in data")
        _create_pie_chart(labels, values, out, title)

    elif chart_type == "scatter":
        x_vals = data.get("x", [])
        y_vals = data.get("y", [])
        if not x_vals or not y_vals:
            raise ValueError("Scatter chart requires 'x' and 'y' in data")
        _create_scatter_chart(x_vals, y_vals, out, title, x_label, y_label)

    else:
        raise ValueError(f"Unknown chart_type: {chart_type}. Use bar, line, pie, or scatter.")

    return str(out), mermaid_md


def _create_bar_chart(
    labels: list[Any],
    values: list[float | int],
    output_path: Path,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = range(len(labels))
    ax.bar(x_pos, values, color="steelblue", edgecolor="white")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([str(l) for l in labels], rotation=45, ha="right")
    if title:
        ax.set_title(title)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _save_fig(fig, output_path)
    plt.close(fig)


def _create_line_chart(
    labels: list[Any],
    values: list[float | int],
    output_path: Path,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(range(len(labels)), values, marker="o", color="steelblue", linewidth=2)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([str(l) for l in labels], rotation=45, ha="right")
    if title:
        ax.set_title(title)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save_fig(fig, output_path)
    plt.close(fig)


def _create_pie_chart(
    labels: list[Any],
    values: list[float | int],
    output_path: Path,
    title: str | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=[str(l) for l in labels], autopct="%1.1f%%", startangle=90)
    if title:
        ax.set_title(title)
    plt.tight_layout()
    _save_fig(fig, output_path)
    plt.close(fig)


def _create_scatter_chart(
    x_vals: list[float | int],
    y_vals: list[float | int],
    output_path: Path,
    title: str | None,
    x_label: str | None,
    y_label: str | None,
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(x_vals, y_vals, color="steelblue", alpha=0.7)
    if title:
        ax.set_title(title)
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save_fig(fig, output_path)
    plt.close(fig)


def _save_fig(fig: plt.Figure, output_path: Path) -> None:
    ext = output_path.suffix.lower()
    if ext == ".svg":
        fig.savefig(output_path, format="svg", bbox_inches="tight")
    else:
        fig.savefig(output_path, format="png", dpi=150, bbox_inches="tight")


def _bar_to_mermaid_xychart(labels: list[Any], values: list[float | int], title: str | None) -> str:
    """Generate Mermaid xychart-beta for bar-style data."""
    x_items = ", ".join(f'"{l}"' if " " in str(l) else str(l) for l in labels)
    y_vals = ", ".join(str(v) for v in values)
    lines = [
        "```mermaid",
        "xychart-beta",
        f"    x-axis [{x_items}]",
        f"    bar [{y_vals}]",
    ]
    if title:
        lines.insert(2, f'    title "{title}"')
    lines.append("```")
    return "\n".join(lines)


def _line_to_mermaid_xychart(labels: list[Any], values: list[float | int], title: str | None) -> str:
    """Generate Mermaid xychart-beta for line-style data."""
    x_items = ", ".join(f'"{l}"' if " " in str(l) else str(l) for l in labels)
    y_vals = ", ".join(str(v) for v in values)
    lines = [
        "```mermaid",
        "xychart-beta",
        f"    x-axis [{x_items}]",
        f"    line [{y_vals}]",
    ]
    if title:
        lines.insert(2, f'    title "{title}"')
    lines.append("```")
    return "\n".join(lines)
