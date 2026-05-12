"""CSS for PDF: clear tables, images, TOC, and layout."""

PDF_CSS = """
@page {
  size: A4;
  margin: 2cm;
  @bottom-center {
    content: counter(page) " / " counter(pages);
    font-size: 9pt;
    color: #666;
  }
}

body {
  font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
  font-size: 11pt;
  line-height: 1.5;
  color: #1a1a1a;
}

/* Table of contents */
#toc {
  break-after: page;
  margin-bottom: 2em;
}

.toc-title {
  font-size: 18pt;
  margin-bottom: 1em;
  color: #222;
  border-bottom: 2px solid #333;
  padding-bottom: 0.3em;
}

.toc-list {
  list-style: none;
  padding-left: 0;
}

.toc-list li {
  margin: 0.35em 0;
  padding: 0.15em 0;
  border-bottom: 1px dotted #ccc;
}

.toc-link {
  text-decoration: none;
  color: #1a1a1a;
}

.toc-link::after {
  content: target-counter(attr(href), page);
  float: right;
  font-weight: normal;
  color: #555;
}

.toc-sep {
  margin: 1.5em 0;
  border: none;
  border-top: 1px solid #ddd;
}

/* Headings */
h1, h2, h3, h4, h5, h6 {
  break-after: avoid;
  color: #222;
  font-weight: 600;
}

h1 { font-size: 18pt; margin-top: 1.2em; margin-bottom: 0.6em; }
h2 { font-size: 14pt; margin-top: 1em; margin-bottom: 0.5em; }
h3 { font-size: 12pt; margin-top: 0.8em; margin-bottom: 0.4em; }
h4, h5, h6 { font-size: 11pt; margin-top: 0.6em; margin-bottom: 0.3em; }

/* Tables: clear and readable */
table {
  width: 100%;
  border-collapse: collapse;
  break-inside: avoid;
  margin: 1em 0;
  font-size: 10pt;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

thead {
  background: #2c3e50;
  color: #fff;
}

th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  border: 1px solid #1a252f;
}

td {
  padding: 8px 12px;
  border: 1px solid #ddd;
}

tbody tr:nth-child(even) {
  background: #f8f9fa;
}

tbody tr:hover {
  background: #eef1f5;
}

/* Images and figures */
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 1em auto;
  break-inside: avoid;
}

figure {
  margin: 1.5em 0;
  break-inside: avoid;
}

figure img {
  margin: 0.5em auto;
}

figcaption {
  font-size: 9pt;
  color: #555;
  text-align: center;
  margin-top: 0.5em;
}

/* Code and pre (text / XML) */
pre, .text-content, .xml-content {
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 9pt;
  line-height: 1.4;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  break-inside: avoid;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.text-document .text-content,
.xml-document .xml-content {
  max-height: none;
}

/* Lists */
ul, ol {
  margin: 0.5em 0;
  padding-left: 1.5em;
}

li {
  margin: 0.25em 0;
}

/* Paragraphs */
p {
  margin: 0.5em 0;
}

/* Links */
a {
  color: #2563eb;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

/* Blockquote */
blockquote {
  margin: 1em 0;
  padding: 0.5em 1em;
  border-left: 4px solid #2563eb;
  background: #f8fafc;
  color: #334155;
}

/* Code inline */
code {
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  font-size: 0.95em;
  background: #f1f5f9;
  padding: 0.15em 0.4em;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
}

/* Page break control */
.break-before { break-before: page; }
.break-after { break-after: page; }
.avoid-break { break-inside: avoid; }
"""

# Simplified CSS for xhtml2pdf (pure Python, no WeasyPrint-specific features)
PDF_CSS_XHTML2PDF = """
body { font-family: Helvetica, Arial, sans-serif; font-size: 11pt; line-height: 1.5; color: #1a1a1a; }
#toc { margin-bottom: 2em; page-break-after: always; }
.toc-title { font-size: 18pt; margin-bottom: 1em; color: #222; border-bottom: 2px solid #333; padding-bottom: 0.3em; }
.toc-list { list-style: none; padding-left: 0; }
.toc-list li { margin: 0.35em 0; padding: 0.15em 0; border-bottom: 1px dotted #ccc; }
.toc-link { text-decoration: none; color: #1a1a1a; }
.toc-sep { margin: 1.5em 0; border: none; border-top: 1px solid #ddd; }
h1, h2, h3, h4, h5, h6 { color: #222; font-weight: bold; }
h1 { font-size: 18pt; margin-top: 1.2em; margin-bottom: 0.6em; }
h2 { font-size: 14pt; margin-top: 1em; margin-bottom: 0.5em; }
h3 { font-size: 12pt; margin-top: 0.8em; margin-bottom: 0.4em; }
h4, h5, h6 { font-size: 11pt; margin-top: 0.6em; margin-bottom: 0.3em; }
table { width: 100%; border-collapse: collapse; margin: 1em 0; font-size: 10pt; }
thead { background: #2c3e50; color: #fff; }
th { padding: 10px 12px; text-align: left; font-weight: bold; border: 1px solid #1a252f; }
td { padding: 8px 12px; border: 1px solid #ddd; }
tbody tr.even { background: #f8f9fa; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
pre, .text-content, .xml-content { font-family: Courier, monospace; font-size: 9pt; line-height: 1.4; background: #f5f5f5; border: 1px solid #e0e0e0; padding: 12px; white-space: pre-wrap; }
ul, ol { margin: 0.5em 0; padding-left: 1.5em; }
li { margin: 0.25em 0; }
p { margin: 0.5em 0; }
a { color: #2563eb; text-decoration: none; }
blockquote { margin: 1em 0; padding: 0.5em 1em; border-left: 4px solid #2563eb; background: #f8fafc; color: #334155; }
code { font-family: Courier, monospace; font-size: 0.95em; background: #f1f5f9; padding: 0.15em 0.4em; border: 1px solid #e2e8f0; }
"""
