"""Inject table of contents and heading IDs into HTML for PDF."""

import re


def _make_id(text: str, seen: dict[str, int]) -> str:
    base = re.sub(r"[^\w\s-]", "", text).strip().lower()
    base = re.sub(r"[-\s]+", "-", base)[:50] or "section"
    seen[base] = seen.get(base, 0) + 1
    return f"{base}-{seen[base]}" if seen[base] > 1 else base


def add_heading_ids_and_collect_toc(html: str, toc_depth: int = 3) -> tuple[str, list[tuple[int, str, str]]]:
    """
    Add id attributes to h1–h6 and return (modified_html, list of (level, id, text) for TOC).
    """
    pattern = re.compile(
        r"<(h[1-6])(\s[^>]*)?>([^<]*)</\1>",
        re.IGNORECASE | re.DOTALL,
    )
    seen: dict[str, int] = {}
    toc: list[tuple[int, str, str]] = []

    def repl(m: re.Match) -> str:
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        level = int(tag[1])
        text = re.sub(r"<[^>]+>", "", inner).strip()
        if not text or level > toc_depth:
            return m.group(0)
        tid = _make_id(text, seen)
        toc.append((level, tid, text))
        if attrs and "id=" in attrs:
            return m.group(0)
        return f'<{tag} id="{tid}"{attrs}>{inner}</{tag}>'

    result = pattern.sub(repl, html)
    return result, toc


def build_toc_html(headings: list[tuple[int, str, str]]) -> str:
    """Generate TOC HTML; WeasyPrint will fill page numbers via target-counter CSS."""
    if not headings:
        return ""

    lines = [
        '<nav id="toc" role="doc-toc">',
        '<h2 class="toc-title">Table of Contents</h2>',
        '<ul class="toc-list">',
    ]
    for level, tid, text in headings:
        indent = (level - 1) * 1.5
        lines.append(f'<li class="toc-level-{level}" style="margin-left: {indent}em">')
        lines.append(f'<a href="#{tid}" class="toc-link">{text}</a>')
        lines.append("</li>")
    lines.append("</ul>")
    lines.append("</nav>")
    return "\n".join(lines)


def inject_toc(html: str, toc_depth: int = 3) -> str:
    """Add heading ids and inject TOC after <body>. Returns full HTML."""
    html_with_ids, headings = add_heading_ids_and_collect_toc(html, toc_depth)
    toc_block = build_toc_html(headings)
    if "<body" in html_with_ids.lower():
        html_with_ids = re.sub(
            r"(<body[^>]*>)",
            r"\1\n" + toc_block + '\n<hr class="toc-sep" />',
            html_with_ids,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        html_with_ids = f"<body>\n{toc_block}\n<hr class=\"toc-sep\" />\n{html_with_ids}\n</body>"
    return html_with_ids
