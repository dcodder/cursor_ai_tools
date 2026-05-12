"""Mermaid diagram rendering – Render Mermaid code to PNG or SVG via mermaid-cli."""

import shutil
import subprocess
import tempfile
from pathlib import Path


def render_mermaid_to_image(
    mermaid_code: str,
    output_path: str,
    theme: str = "default",
) -> str:
    """Render Mermaid diagram code to PNG or SVG.

    Uses @mermaid-js/mermaid-cli (mmdc) via npx. Requires Node.js.

    Args:
        mermaid_code: Raw Mermaid diagram code.
        output_path: Path for output file (extension determines PNG vs SVG).
        theme: "default", "dark", or "neutral".

    Returns:
        Absolute path to created image.
    """
    out = Path(output_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".mmd",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(mermaid_code)
        input_path = f.name

    try:
        _run_mmdc(input_path, str(out), theme)
        return str(out)
    finally:
        Path(input_path).unlink(missing_ok=True)


def _run_mmdc(input_path: str, output_path: str, theme: str) -> None:
    """Run mermaid-cli (mmdc) to render diagram."""
    mmdc = shutil.which("mmdc")
    if mmdc:
        cmd = [mmdc, "-i", input_path, "-o", output_path, "-t", theme]
    else:
        # Fall back to npx
        cmd = [
            "npx",
            "-y",
            "@mermaid-js/mermaid-cli",
            "-i", input_path,
            "-o", output_path,
            "-t", theme,
        ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"mermaid-cli failed: {result.stderr or result.stdout or 'Unknown error'}"
        )
