# Diagrams MCP Server

MCP server for creating diagrams (Mermaid), tables, figures, and data charts. Outputs both markdown and image files (PNG, SVG).

## Requirements

- **Python 3.10+** (via `uv` or `pip`)
- **Node.js** (for Mermaid image rendering via `@mermaid-js/mermaid-cli`)

## Installation

```bash
cd diagrams-mcp-server
uv sync
```

## Tools

### 1. `create_table`

Generate a markdown or HTML table from structured data.

| Parameter | Type | Description |
|-----------|------|-------------|
| `headers` | list[str] | Column headers |
| `rows` | list[list] | Row data (each row = list of cell values) |
| `format` | str | `"markdown"` or `"html"` |
| `caption` | str (optional) | Table caption |

**Example:**

```json
{
  "headers": ["Name", "Score", "Grade"],
  "rows": [["Alice", 95, "A"], ["Bob", 82, "B"]],
  "format": "markdown",
  "caption": "Student results"
}
```

---

### 2. `create_chart`

Generate a data chart and save as PNG or SVG.

| Parameter | Type | Description |
|-----------|------|-------------|
| `chart_type` | str | `"bar"`, `"line"`, `"pie"`, or `"scatter"` |
| `data` | object | `{"labels": [...], "values": [...]}` or `{"x": [...], "y": [...]}` |
| `output_path` | str | Path for output file (.png or .svg) |
| `title` | str (optional) | Chart title |
| `x_label` | str (optional) | X-axis label |
| `y_label` | str (optional) | Y-axis label |

**Example (bar chart):**

```json
{
  "chart_type": "bar",
  "data": {"labels": ["Jan", "Feb", "Mar"], "values": [100, 150, 120]},
  "output_path": "D:/AI_Work/generated/sales.png",
  "title": "Monthly Sales"
}
```

**Example (scatter):**

```json
{
  "chart_type": "scatter",
  "data": {"x": [1, 2, 3, 4], "y": [2, 4, 3, 5]},
  "output_path": "D:/AI_Work/generated/scatter.svg"
}
```

For bar and line charts, the tool also returns optional Mermaid `xychart-beta` markdown.

---

### 3. `create_mermaid_diagram`

Generate a Mermaid diagram and optionally render to image.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mermaid_code` | str | Raw Mermaid diagram code |
| `output_path` | str (optional) | Path for image when format is png/svg/both |
| `format` | str | `"markdown_only"`, `"png"`, `"svg"`, or `"both"` |
| `theme` | str (optional) | `"default"`, `"dark"`, or `"neutral"` |

**Example:**

```json
{
  "mermaid_code": "flowchart LR\n  A --> B --> C",
  "output_path": "D:/AI_Work/generated/diagram",
  "format": "both",
  "theme": "default"
}
```

Returns markdown fenced block and, when format is png/svg/both, absolute path(s) to rendered image(s).

---

### 4. `render_mermaid_to_image`

Render existing Mermaid code to PNG or SVG.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mermaid_code` | str | Mermaid diagram code |
| `output_path` | str | Path for output (.png or .svg) |
| `theme` | str (optional) | `"default"`, `"dark"`, or `"neutral"` |

**Example:**

```json
{
  "mermaid_code": "pie title Distribution\n  \"A\" : 40\n  \"B\" : 60",
  "output_path": "D:/AI_Work/generated/pie.png"
}
```

## Cursor Configuration

Add to `.cursor/mcp.json`:

```json
"diagrams-mcp-server": {
  "command": "uv",
  "args": ["--directory", "D:/AI_Work/diagrams-mcp-server", "run", "server.py"]
}
```

## Mermaid Image Rendering

Mermaid diagrams are rendered via `@mermaid-js/mermaid-cli` (mmdc). The server will:

1. Use `mmdc` from PATH if installed globally
2. Fall back to `npx -y @mermaid-js/mermaid-cli` otherwise

Ensure Node.js is installed for image export. Tables and charts (matplotlib) work without Node.js.
