#!/usr/bin/env python3
"""
Markdown Converter
==================

Converts a Markdown file into a styled HTML page. Standard library only,
no third-party packages.

Supported Markdown:
  - Headings: # ## ### (up to ######)
  - Bold **text**, italic *text*, inline `code`
  - Links [text](url) and images ![alt](url)
  - Fenced code blocks (```) with optional language label
  - Unordered lists (- or *) and ordered lists (1. 2. 3.)
  - Blockquotes (> ...)
  - Horizontal rules (---)
  - Paragraphs separated by blank lines

Everything else passes through as paragraph text. Raw HTML in the input
is escaped, so it can never break the page.

Usage:
    python markdown_converter.py notes.md --output notes.html
    python markdown_converter.py notes.md --output notes.html --title "My Notes"
    python markdown_converter.py notes.md   (prints HTML to stdout)

TechAbout Python Developer task 9 - Markdown Converter (ZR-26-00754).
"""

import argparse
import html
import re
import sys

esc = html.escape

# inline patterns (applied after escaping, in this order)
CODE_SPAN_RE = re.compile(r"`([^`]+?)`")
BOLD_RE = re.compile(r"\*\*([^*]+?)\*\*")
ITALIC_RE = re.compile(r"\*([^*]+?)\*")
IMAGE_RE = re.compile(r"!\[([^\]]*?)\]\(([^)]+?)\)")
LINK_RE = re.compile(r"\[([^\]]+?)\]\(([^)]+?)\)")

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
HR_RE = re.compile(r"^\s*---\s*$")
UL_RE = re.compile(r"^\s*[-*]\s+(.*)$")
OL_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
QUOTE_RE = re.compile(r"^\s*>\s?(.*)$")


def inline(text):
    """Apply inline formatting to already-escaped text."""
    # protect code spans first so * and [ inside code are untouched
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    text = CODE_SPAN_RE.sub(stash, text)
    text = IMAGE_RE.sub(r'<img src="\2" alt="\1">', text)
    text = LINK_RE.sub(r'<a href="\2">\1</a>', text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    text = ITALIC_RE.sub(r"<em>\1</em>", text)
    for i, code in enumerate(codes):
        text = text.replace("\x00%d\x00" % i, "<code>%s</code>" % code)
    return text


def convert_body(markdown):
    """Convert Markdown body text to HTML fragments (no <html> wrapper)."""
    lines = markdown.split("\n")
    out = []
    paragraph = []
    in_code = False
    code_lines = []
    code_lang = ""
    list_open = None  # "ul" or "ol"

    def flush_paragraph():
        if paragraph:
            out.append("<p>%s</p>" % inline(" ".join(paragraph)))
            paragraph.clear()

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</%s>" % list_open)
            list_open = None

    def open_list(kind):
        nonlocal list_open
        if list_open != kind:
            close_list()
            out.append("<%s>" % kind)
            list_open = kind

    for raw in lines:
        line = raw.rstrip("\n")

        # fenced code blocks
        if line.strip().startswith("```"):
            if in_code:
                out.append("<pre><code%s>%s</code></pre>" % (
                    (' class="language-%s"' % esc(code_lang)) if code_lang else "",
                    esc("\n".join(code_lines))))
                in_code = False
                code_lines = []
                code_lang = ""
            else:
                flush_paragraph()
                close_list()
                in_code = True
                code_lang = line.strip()[3:].strip()
            continue
        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            close_list()
            continue

        m = HEADING_RE.match(line)
        if m:
            flush_paragraph()
            close_list()
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, inline(m.group(2).strip()), level))
            continue

        if HR_RE.match(line):
            flush_paragraph()
            close_list()
            out.append("<hr>")
            continue

        m = QUOTE_RE.match(line)
        if m:
            flush_paragraph()
            close_list()
            out.append("<blockquote>%s</blockquote>" % inline(m.group(1)))
            continue

        m = UL_RE.match(line)
        if m:
            flush_paragraph()
            open_list("ul")
            out.append("<li>%s</li>" % inline(m.group(1)))
            continue

        m = OL_RE.match(line)
        if m:
            flush_paragraph()
            open_list("ol")
            out.append("<li>%s</li>" % inline(m.group(1)))
            continue

        paragraph.append(esc(line.strip()))

    flush_paragraph()
    close_list()
    if in_code:  # unclosed fence: still emit what we have
        out.append("<pre><code>%s</code></pre>" % esc("\n".join(code_lines)))
    return "\n".join(out)


def build_page(body_html, title="Markdown Document"):
    """Wrap body HTML in a styled page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;color:#222;line-height:1.6;}
h1,h2,h3{color:#1f497d;}
pre{background:#f4f4f4;padding:12px;border-radius:6px;overflow-x:auto;}
code{background:#f4f4f4;padding:2px 5px;border-radius:4px;}
pre code{background:none;padding:0;}
blockquote{border-left:4px solid #1f497d;margin:16px 0;padding:8px 16px;background:#f2f6fb;}
table{border-collapse:collapse;}
img{max-width:100%%;}
a{color:#1f497d;}
</style>
</head>
<body>
%s
</body>
</html>""" % (esc(title), body_html)


def convert_file(input_path, output_path=None, title=None):
    """Convert a Markdown file to HTML. Returns the page string."""
    with open(input_path, "r", encoding="utf-8") as fh:
        markdown = fh.read()
    if title is None:
        # first heading becomes the page title, else the file name
        m = HEADING_RE.search(markdown)
        title = m.group(2).strip() if m else input_path
    page = build_page(convert_body(markdown), title)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(page)
    return page


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Convert a Markdown file into an HTML page.")
    parser.add_argument("markdown_file", help="Path to the input .md file")
    parser.add_argument("--output", default="",
                        help="Write the HTML page to this file")
    parser.add_argument("--title", default="",
                        help="Page title (default: first heading)")
    args = parser.parse_args(argv)

    try:
        page = convert_file(args.markdown_file, args.output or None,
                            args.title or None)
    except FileNotFoundError:
        print("Error: file not found: %s" % args.markdown_file, file=sys.stderr)
        return 1

    if args.output:
        print("Converted %s -> %s" % (args.markdown_file, args.output))
    else:
        print(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
